import json
import os
from sentence_transformers import SentenceTransformer, util
import warnings
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"  # 0 = all logs, 1 = filter INFO, 2 = filter WARNING, 3 = filter ERROR
warnings.filterwarnings("ignore")

class LeafletKBAProcess:
    def __init__(self, repo_file="kba_question_repo.json", model_name="all-MiniLM-L6-v2"):
        self.repo_file = repo_file
        self.model = SentenceTransformer(model_name)

        # Initialize repo if not exists
        if not os.path.exists(self.repo_file):
            with open(self.repo_file, "w") as f:
                json.dump({}, f)

    def _load_repo(self):
        with open(self.repo_file, "r") as f:
            return json.load(f)

    def _save_repo(self, repo):
        with open(self.repo_file, "w") as f:
            json.dump(repo, f, indent=4)

    def store_kba(self, user_data: dict):
        """
        Store KBA Q&A for a user in the flat format:
        {
          "userid": 90018,
          "question-1": "What is your nickname",
          "answer-1": "tim",
          "question-2": "what is your ssn firt 5 digit",
          "answer-2": "34534"
        }
        """
        if "userid" not in user_data:
            raise ValueError("user_data must include 'userid'")

        userid = str(user_data["userid"])
        repo = self._load_repo()
        repo[userid] = user_data
        self._save_repo(repo)
        return {"status": True, "msg": f"User id {userid} stored in KBA repository"}

        #print(f"KBA stored for user {userid}")
    
    def verify_kba(self, userid, user_answers: dict, threshold=0.80, min_match_ratio=1.0):
        repo = self._load_repo()
        userid = str(userid)

        if userid not in repo:
            return {"status": False, "msg": f"No pre-KBA process for user: {userid}"}

        stored_data = repo[userid]
        total_questions = sum(1 for k in stored_data if k.startswith("question-"))
        correct_matches = 0
        not_part_of_kba = []

        # Check each submitted question/answer
        for i in range(1, total_questions + 1):
            q_key = f"question-{i}"
            a_key = f"answer-{i}"

            if q_key not in stored_data or a_key not in stored_data:
                continue

            stored_q = stored_data[q_key].strip().lower()
            stored_a = stored_data[a_key]
            is_numeric_builtin = str(stored_a).isnumeric()

            #print(f"stored_a : {stored_a} -- {is_numeric_builtin}")
            given_q = user_answers.get(q_key, "").strip().lower()
            given_a = user_answers.get(a_key, "")

            # If question text does not match exactly
            if given_q != stored_q:
                not_part_of_kba.append(user_answers.get(q_key, f"Unknown question {i}"))
                continue
            
            if is_numeric_builtin and stored_a != given_a:
               continue

            # Compare answers semantically
            emb_stored = self.model.encode(stored_a, convert_to_tensor=True)
            emb_given = self.model.encode(given_a, convert_to_tensor=True)
            similarity = float(util.cos_sim(emb_stored, emb_given))
                         

            if similarity >= threshold:
                correct_matches += 1

        match_ratio = correct_matches / total_questions if total_questions > 0 else 0

        result = {
            "status": match_ratio >= min_match_ratio,
            "msg": (
                f"Verification SUCCESS ({correct_matches}/{total_questions} correct)"
                if match_ratio >= min_match_ratio
                else f"Verification FAILURE ({correct_matches}/{total_questions} correct)"
            ),
            "KBA rejection": not_part_of_kba
        }
        return result
    
# Example usage
if __name__ == "__main__":
    kba = LeafletKBAProcess()

    # Step 1: Store KBA
    kba.store_kba({
        "userid": 90018,
        "question-1": "What is your nickname",
        "answer-1": "tim",
        "question-2": "what is your ssn firt 5 digit",
        "answer-2": "34534",
        "question-3": "your birth place is",
        "answer-3": "Hemilton",
        "question-4": "Your most like food",
        "answer-4": "Pasta",
        "question-5": "What is your first school name",
        "answer-5": "KVM"
    })
   
    stored_result = kba.store_kba({
        "userid": 90020,
        "question-1": "What is your nickname",
        "answer-1": "Groke",
        "question-2": "what is your ssn firt 5 digit",
        "answer-2": "90998",
        "question-3": "your birth place is",
        "answer-3": "Boston",
        "question-4": "Your most like food",
        "answer-4": "Nuges",
        "question-5": "What is your first school name",
        "answer-5": "First Convt"
    })
    print(stored_result)
    # Step 2: Verify KBA
    result = kba.verify_kba(90020, {
        "userid": 90020,
        "question-1": "What is your nickname",
        "answer-1": "Groke",
        "question-2": "what is your ssn firt 5 digit",
        "answer-2": "90998",
        "question-3": "your birth place is",
        "answer-3": "Boston",
        "question-4": "Your most like food",
        "answer-4": "Nuges",
        "question-5": "What is your first school name",
        "answer-5": "First Convt"
    })
    print(result)
