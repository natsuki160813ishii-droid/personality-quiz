import json
import random
import sys

class QuizEngine:
    def __init__(self, questions_file):
        self.questions = self._load_questions(questions_file)
        self.scores = {
            "Logic": 0,
            "Empathy": 0,
            "Daring": 0,
            "Prudence": 0
        }
        self.profiles = {
            "Logic": ("賢者", "論理的で冷静な判断ができる"),
            "Empathy": ("交渉人", "他者の心に寄り添い、和を重んじる"),
            "Daring": ("勇者", "リスクを恐れず、直感で道を切り拓く"),
            "Prudence": ("守護者", "慎重に準備を整え、確実性を重視する")
        }

    def _load_questions(self, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"エラー: 質問ファイルの読み込みに失敗しました ({e})")
            sys.exit(1)

    def shuffle_questions(self):
        random.shuffle(self.questions)

    def start_quiz(self):
        print("--- 性格診断エンジン プロトタイプ ---")
        print("10の質問に 1～4 の番号で答えてください。\n")

        for i, q in enumerate(self.questions[:10], 1):
            print(f"Q{i}: {q['text']}")
            for idx, choice in enumerate(q['choices'], 1):
                print(f"  {idx}. {choice['text']}")
            
            answer = self._get_valid_input()
            self._record_answer(q['choices'][answer - 1])
            print()

    def _get_valid_input(self):
        while True:
            try:
                choice = int(input("回答 (1-4): "))
                if 1 <= choice <= 4:
                    return choice
                else:
                    print("1から4の間で入力してください。")
            except ValueError:
                print("数字を入力してください。")

    def _record_answer(self, choice):
        for attr, points in choice['points'].items():
            if attr in self.scores:
                self.scores[attr] += points

    def display_result(self):
        # 最もスコアが高い属性を特定
        top_attr = max(self.scores, key=self.scores.get)
        profile_name, description = self.profiles[top_attr]

        print("--- 診断結果 ---")
        print(f"あなたのタイプは: 【{profile_name}】")
        print(f"特徴: {description}")
        print("\nパラメータ詳細:")
        for attr, score in self.scores.items():
            print(f"  - {attr}: {score}")

if __name__ == "__main__":
    engine = QuizEngine('questions.json')
    engine.shuffle_questions()
    engine.start_quiz()
    engine.display_result()
