# expert_system.py
class HexagonalExpertSystem:
    def __init__(self):
        self.code_analyzer = CodeAnalyzer()
        self.pattern_matcher = PatternMatcher()
        self.rule_engine = RuleEngine()
        
    def analyze_codebase(self):
        """Analyse complète de la codebase"""
        analysis = {
            'architecture_patterns': self.detect_patterns(),
            'code_smells': self.detect_smells(),
            'best_practices': self.check_best_practices(),
            'test_coverage': self.analyze_tests(),
            'dependencies': self.map_dependencies()
        }
        return analysis
    
    def suggest_improvements(self, file_path):
        """Suggestions contextuelles"""
        file_analysis = self.code_analyzer.analyze_file(file_path)
        suggestions = []
        
        # Règles expertes
        if file_analysis['layer'] == 'domain':
            suggestions.extend(self.domain_layer_rules(file_analysis))
        elif file_analysis['layer'] == 'infrastructure':
            suggestions.extend(self.infrastructure_rules(file_analysis))
            
        return suggestions