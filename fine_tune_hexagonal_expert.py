import json
import torch
from transformers import (
    AutoTokenizer, 
    AutoModelForCausalLM, 
    TrainingArguments, 
    Trainer,
    DataCollatorForLanguageModeling
)
from datasets import Dataset
from peft import LoraConfig, get_peft_model, TaskType
import os

class HexagonalFineTuner:
    def __init__(self, base_model="microsoft/DialoGPT-small", output_dir="./hexagonal-expert"):
        self.base_model = base_model
        self.output_dir = output_dir
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"🔥 Utilisation: {self.device}")
        
    def load_training_data(self, data_file="hexagonal_training_data.json"):
        """Charger les données d'entraînement"""
        print(f"📚 Chargement de {data_file}")
        
        with open(data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Formater pour l'entraînement
        formatted_data = []
        for item in data:
            # Format simple question-réponse
            text = f"Question: {item['instruction']}\nRéponse: {item['output']}<|endoftext|>"
            formatted_data.append({"text": text})
        
        print(f"✅ {len(formatted_data)} exemples chargés")
        return Dataset.from_list(formatted_data)
    
    def setup_model_and_tokenizer(self):
        """Configurer le modèle et le tokenizer"""
        print("🤖 Chargement du modèle de base...")
        
        try:
            # Tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(self.base_model)
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            
            # Modèle
            self.model = AutoModelForCausalLM.from_pretrained(
                self.base_model,
                torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                device_map="auto" if torch.cuda.is_available() else None
            )
            
            print(f"✅ Modèle {self.base_model} chargé avec succès")
            
            # Configuration LoRA optimisée pour DialoGPT
            lora_config = LoraConfig(
                task_type=TaskType.CAUSAL_LM,
                inference_mode=False,
                r=4,  # Rang réduit pour RTX 3080
                lora_alpha=16,
                lora_dropout=0.1,
                target_modules=["c_attn", "c_proj"]  # Modules spécifiques à GPT
            )
            
            # Appliquer LoRA
            self.model = get_peft_model(self.model, lora_config)
            print("🔧 LoRA configuré")
            
            # Afficher les paramètres entraînables
            trainable_params = sum(p.numel() for p in self.model.parameters() if p.requires_grad)
            total_params = sum(p.numel() for p in self.model.parameters())
            print(f"📊 Paramètres entraînables: {trainable_params:,} / {total_params:,} ({100 * trainable_params / total_params:.2f}%)")
            
        except Exception as e:
            print(f"❌ Erreur lors du chargement du modèle: {e}")
            raise
    
    def tokenize_data(self, dataset):
        """Tokeniser les données"""
        print("🔤 Tokenisation...")
        
        def tokenize_function(examples):
            return self.tokenizer(
                examples["text"],
                truncation=True,
                padding=True,
                max_length=256,  # Réduit pour RTX 3080
                return_tensors="pt"
            )
        
        tokenized_dataset = dataset.map(
            tokenize_function,
            batched=True,
            remove_columns=dataset.column_names
        )
        
        return tokenized_dataset
    
    def fine_tune(self, dataset, epochs=2, batch_size=2):
        """Lancer le fine-tuning avec paramètres corrigés"""
        print("🚀 Début du fine-tuning...")
        
        # Arguments d'entraînement CORRIGÉS
        training_args = TrainingArguments(
            output_dir=self.output_dir,
            num_train_epochs=epochs,
            per_device_train_batch_size=batch_size,
            per_device_eval_batch_size=batch_size,
            warmup_steps=50,
            logging_steps=5,
            save_steps=100,
            eval_strategy="no",  # CORRIGÉ: eval_strategy au lieu de evaluation_strategy
            save_total_limit=1,
            prediction_loss_only=True,
            remove_unused_columns=False,
            dataloader_pin_memory=False,
            gradient_accumulation_steps=8,
            fp16=torch.cuda.is_available(),
            learning_rate=5e-5,
            weight_decay=0.01,
            lr_scheduler_type="linear",
            report_to=None,
            max_grad_norm=1.0,
            dataloader_num_workers=0
        )
        
        # Data collator
        data_collator = DataCollatorForLanguageModeling(
            tokenizer=self.tokenizer,
            mlm=False
        )
        
        # Trainer
        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=dataset,
            data_collator=data_collator,
            tokenizer=self.tokenizer
        )
        
        try:
            # Entraînement
            print("🎯 Entraînement en cours...")
            trainer.train()
            
            # Sauvegarder
            trainer.save_model()
            self.tokenizer.save_pretrained(self.output_dir)
            
            print(f"✅ Modèle sauvegardé dans {self.output_dir}")
            
        except RuntimeError as e:
            if "out of memory" in str(e):
                print("💾 Mémoire GPU insuffisante. Tentative avec des paramètres réduits...")
                return self.fine_tune_reduced_memory(dataset)
            else:
                raise e
    
    def fine_tune_reduced_memory(self, dataset):
        """Fine-tuning avec mémoire réduite"""
        print("🔧 Mode mémoire réduite activé...")
        
        # Paramètres très conservateurs
        training_args = TrainingArguments(
            output_dir=self.output_dir,
            num_train_epochs=1,
            per_device_train_batch_size=1,
            gradient_accumulation_steps=16,
            fp16=True,
            learning_rate=3e-5,
            warmup_steps=20,
            logging_steps=10,
            save_steps=50,
            max_grad_norm=0.5,
            dataloader_num_workers=0,
            report_to=None,
            eval_strategy="no"  # CORRIGÉ
        )
        
        data_collator = DataCollatorForLanguageModeling(
            tokenizer=self.tokenizer,
            mlm=False
        )
        
        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=dataset,
            data_collator=data_collator,
            tokenizer=self.tokenizer
        )
        
        trainer.train()
        trainer.save_model()
        self.tokenizer.save_pretrained(self.output_dir)
        print(f"✅ Modèle sauvegardé (mode réduit)")
    
    def test_model(self, prompt="Explique-moi l'architecture hexagonale"):
        """Tester le modèle fine-tuné"""
        print("🧪 Test du modèle...")
        
        try:
            # Charger le modèle fine-tuné
            from peft import PeftModel
            
            base_model = AutoModelForCausalLM.from_pretrained(
                self.base_model,
                torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32
            )
            model = PeftModel.from_pretrained(base_model, self.output_dir)
            tokenizer = AutoTokenizer.from_pretrained(self.output_dir)
            
            if tokenizer.pad_token is None:
                tokenizer.pad_token = tokenizer.eos_token
            
            # Préparer le prompt
            full_prompt = f"Question: {prompt}\nRéponse:"
            
            # Tokeniser
            inputs = tokenizer(full_prompt, return_tensors="pt")
            if torch.cuda.is_available():
                inputs = {k: v.cuda() for k, v in inputs.items()}
                model = model.cuda()
            
            # Générer
            with torch.no_grad():
                outputs = model.generate(
                    **inputs,
                    max_new_tokens=150,
                    temperature=0.7,
                    do_sample=True,
                    pad_token_id=tokenizer.eos_token_id,
                    eos_token_id=tokenizer.eos_token_id
                )
            
            # Décoder
            response = tokenizer.decode(outputs[0], skip_special_tokens=True)
            print("🤖 Réponse du modèle fine-tuné:")
            print(response[len(full_prompt):])
            
        except Exception as e:
            print(f"❌ Erreur lors du test: {e}")
            print("💡 Le modèle a été sauvegardé mais le test a échoué")

def main():
    # Vérifier que les données existent
    if not os.path.exists("hexagonal_training_data.json"):
        print("❌ Fichier hexagonal_training_data.json non trouvé!")
        print("Lancez d'abord: python create_training_data.py")
        return
    
    try:
        # Initialiser le fine-tuner
        finetuner = HexagonalFineTuner()
        
        # Charger les données
        dataset = finetuner.load_training_data()
        
        # Limiter le dataset pour éviter les problèmes de mémoire
        if len(dataset) > 30:  # Encore plus réduit
            dataset = dataset.select(range(30))
            print(f"🔢 Dataset réduit à {len(dataset)} exemples pour l'entraînement")
        
        # Configurer le modèle
        finetuner.setup_model_and_tokenizer()
        
        # Tokeniser
        tokenized_dataset = finetuner.tokenize_data(dataset)
        
        # Fine-tuner
        finetuner.fine_tune(tokenized_dataset, epochs=1, batch_size=1)  # Paramètres très réduits
        
        # Tester
        finetuner.test_model()
        
        print("\n🎉 Fine-tuning terminé!")
        print("Le modèle est maintenant spécialisé sur votre architecture hexagonale!")
        
    except Exception as e:
        print(f"❌ Erreur générale: {e}")
        print("💡 Utilisez l'alternative simple_expert.py qui fonctionne sans fine-tuning")

if __name__ == "__main__":
    main()