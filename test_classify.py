
#Required: pip install transformers keybert sentence-transformers

from keybert import KeyBERT
from transformers import pipeline
import pdfplumber
import re
import string
import nltk
import nltk
from nltk.tokenize import sent_tokenize
from transformers import AutoTokenizer
import math
#from bs4 import BeautifulSoup
from nltk.tokenize import word_tokenize, sent_tokenize

nltk.download('punkt_tab')

class LeafletZeroShotClassifyNoLabel:
    def __init__(self,  max_chunk_tokens=900, top_k_keywords=5):
        model_name="facebook/bart-large-mnli"
        self.model = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
        self.kw_model = KeyBERT('all-MiniLM-L6-v2')
        self.top_k = top_k_keywords
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.max_chunk_tokens = max_chunk_tokens
    
    
    def _preprocess_text(self, text):
        """Basic text cleaning for chunks."""
        text = text.lower()
        #soup = BeautifulSoup(text, 'html.parser')
        #text = soup.get_text()
        text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
        text = text.translate(str.maketrans('', '', string.punctuation))
        text = re.sub(r'\d+', '', text)
        text = re.sub(r'[^a-z\s]', '', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    def _chunk_text(self, long_text):
        """
        Splits a long text into chunks based on sentences, respecting max_chunk_tokens.
        Adds a small overlap to preserve context.
        """
        preprocessed_text = self._preprocess_text(long_text)
        sentences = sent_tokenize(preprocessed_text)
        chunks = []
        current_chunk_sentences = []
        current_chunk_length = 0
        overlap_sentences_count = 2
        for i, sentence in enumerate(sentences):
            sentence_tokens = self.tokenizer.encode(sentence, add_special_tokens=False)
            sentence_length = len(sentence_tokens)
            if current_chunk_length + sentence_length <= self.max_chunk_tokens:
                current_chunk_sentences.append(sentence)
                current_chunk_length += sentence_length
            else:                
                if current_chunk_sentences:
                    chunks.append(" ".join(current_chunk_sentences))
                current_chunk_sentences = sentences[max(0, i - overlap_sentences_count):i] + [sentence]
                current_chunk_length = sum(len(self.tokenizer.encode(s, add_special_tokens=False)) for s in current_chunk_sentences)
                if sentence_length > self.max_chunk_tokens:
                    # Handle extremely long sentences by splitting them if necessary
                    # For simplicity here, we assume sentences are generally manageable.
                    pass


        if current_chunk_sentences: # Add the last chunk
            chunks.append(" ".join(current_chunk_sentences))

        return chunks


    def _read_pdf_text(self, pdf_path):
        text = ""
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                words = page.extract_words()
                line = " ".join(w['text'] for w in words)
                text += line + "\n"
        return text
    
    
    def get_candidate_labels(self, text):
        raw_keywords = self.kw_model.extract_keywords(text, keyphrase_ngram_range=(1, 2), stop_words='english', top_n=self.top_k)
        filtered = [
            kw[0] for kw in raw_keywords
            if len(kw[0].split()) <= 3 and not re.search(r'\d{4,}', kw[0])
        ]
        return filtered


    def classify(self, document_text):
        all_chunk_results = []
        chunk_list = self._chunk_text(document_text)
        for text in chunk_list:
            candidate_labels = self.get_candidate_labels(text)
            result = self.model(text, candidate_labels, multi_label=True)
            all_chunk_results.append(result)
        
        if not all_chunk_results:
            return {'labels': candidate_labels, 'scores': [0.0] * len(candidate_labels)}

        aggregated_scores = {label: [] for label in candidate_labels}
        # Collect scores for each label from all chunks
        for chunk_result in all_chunk_results:
            for i, label in enumerate(chunk_result['labels']):
                aggregated_scores[label].append(chunk_result['scores'][i])

        return aggregated_scores
        
    def process_classify(self, pdf_path):
        raw_text = self._read_pdf_text(pdf_path)        
        
        result = self.classify(raw_text)       
        
        final_results = []
       
        #item['document'] = pdf_path
        for lb,sc in result.items(): 
            item = {}           
            item['label'] = lb
            item['score'] = sc
            final_results.append(item)

        final_output = {
            "filepath": file_path,
            "classifications": final_results 
        }
        return final_output
        
if __name__ == "__main__":
    clf = LeafletZeroShotClassifyNoLabel(top_k_keywords=3)
    file_path = r"F:\AmazonShare\Conman files\knda.pdf"
    output = clf.process_classify(file_path)
    print("===============output===================")
    print(output)
  
