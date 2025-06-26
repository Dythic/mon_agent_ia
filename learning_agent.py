# learning_agent.py
class LearningCodeAgent:
    def __init__(self):
        self.knowledge_graph = {}
        self.interaction_history = []
        self.patterns_learned = {}
    
    def learn_from_interaction(self, question, answer, feedback):
        """Apprendre des interactions"""
        self.interaction_history.append({
            'question': question,
            'answer': answer,
            'feedback': feedback,
            'timestamp': datetime.now()
        })
        
        # Analyser les patterns
        self.update_knowledge_graph(question, answer)
    
    def update_knowledge_graph(self, question, answer):
        """Construire un graphe de connaissances"""
        entities = extract_entities(question + answer)
        relationships = extract_relationships(entities)
        
        for entity in entities:
            if entity not in self.knowledge_graph:
                self.knowledge_graph[entity] = {
                    'type': classify_entity(entity),
                    'relationships': [],
                    'contexts': []
                }
            
            self.knowledge_graph[entity]['contexts'].append({
                'question': question,
                'answer': answer
            })