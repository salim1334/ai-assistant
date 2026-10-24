"""
Cognitive Analytics Module

This module contains the CognitiveAnalytics class, which provides cognitive analytics
capabilities for advanced AI-driven insights and natural language understanding.
"""

import logging
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, Any, List, Optional, Tuple, Union
import json
import os
import re
from datetime import datetime, timedelta

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CognitiveAnalytics:
    """
    The CognitiveAnalytics class provides methods for advanced AI-driven insights
    and natural language understanding.
    
    It includes functionality for text analysis, sentiment analysis, entity recognition,
    topic modeling, and natural language generation.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the CognitiveAnalytics module.
        
        Args:
            config: Configuration parameters for the module.
        """
        self.config = config or {}
        logger.info("Initializing CognitiveAnalytics module")
        
        # Set default parameters
        self.language = self.config.get("language", "en")
        self.sentiment_threshold = self.config.get("sentiment_threshold", 0.5)
        self.entity_confidence = self.config.get("entity_confidence", 0.6)
        self.topic_count = self.config.get("topic_count", 5)
        self.max_summary_length = self.config.get("max_summary_length", 200)
        
        # Initialize NLP components if available
        self.nlp_initialized = False
        self.sentiment_analyzer = None
        self.entity_recognizer = None
        self.topic_modeler = None
        self.text_summarizer = None
        
        try:
            self._initialize_nlp_components()
            self.nlp_initialized = True
        except Exception as e:
            logger.warning(f"Could not initialize NLP components: {e}")
            logger.info("NLP functionality will be limited")
        
        logger.info("CognitiveAnalytics module initialized successfully")
    
    def _initialize_nlp_components(self):
        """
        Initialize NLP components based on available libraries.
        """
        # Try to import and initialize NLP libraries
        try:
            import nltk
            nltk.download('punkt', quiet=True)
            nltk.download('stopwords', quiet=True)
            nltk.download('wordnet', quiet=True)
            nltk.download('vader_lexicon', quiet=True)
            
            from nltk.sentiment.vader import SentimentIntensityAnalyzer
            self.sentiment_analyzer = SentimentIntensityAnalyzer()
            
            logger.info("NLTK components initialized successfully")
        except ImportError:
            logger.warning("NLTK not available, some NLP functionality will be limited")
        
        # Try to import spaCy for entity recognition
        try:
            import spacy
            try:
                self.entity_recognizer = spacy.load(f"{self.language}_core_web_sm")
            except:
                logger.warning(f"spaCy model for language {self.language} not available")
                try:
                    self.entity_recognizer = spacy.load("en_core_web_sm")
                    logger.info("Loaded default English spaCy model")
                except:
                    logger.warning("No spaCy models available, entity recognition will be limited")
        except ImportError:
            logger.warning("spaCy not available, entity recognition will be limited")
        
        # Try to import gensim for topic modeling
        try:
            import gensim
            self.topic_modeler_available = True
            logger.info("Gensim initialized for topic modeling")
        except ImportError:
            self.topic_modeler_available = False
            logger.warning("Gensim not available, topic modeling will be limited")
    
    def analyze_text(self, text: str, analysis_types: List[str] = None) -> Dict[str, Any]:
        """
        Perform comprehensive text analysis.
        
        Args:
            text: Text to analyze.
            analysis_types: List of analysis types to perform. If None, performs all available analyses.
                Options: 'sentiment', 'entities', 'topics', 'summary', 'keywords', 'readability'
            
        Returns:
            A dictionary containing analysis results.
        """
        logger.info(f"Analyzing text ({len(text)} characters)")
        
        if not text:
            logger.error("No text provided")
            return {"error": "No text provided"}
        
        # Set default analysis types if not provided
        if analysis_types is None:
            analysis_types = ['sentiment', 'entities', 'keywords', 'readability']
            
            # Add topics and summary if text is long enough
            if len(text) > 500:
                analysis_types.extend(['topics', 'summary'])
        
        # Initialize results
        results = {
            "text_length": len(text),
            "word_count": len(text.split())
        }
        
        # Perform requested analyses
        if 'sentiment' in analysis_types:
            sentiment = self.analyze_sentiment(text)
            if "error" not in sentiment:
                results["sentiment"] = sentiment
        
        if 'entities' in analysis_types:
            entities = self.extract_entities(text)
            if "error" not in entities:
                results["entities"] = entities
        
        if 'topics' in analysis_types and len(text) > 500:
            topics = self.extract_topics(text)
            if "error" not in topics:
                results["topics"] = topics
        
        if 'summary' in analysis_types and len(text) > 500:
            summary = self.generate_summary(text)
            if "error" not in summary:
                results["summary"] = summary
        
        if 'keywords' in analysis_types:
            keywords = self.extract_keywords(text)
            if "error" not in keywords:
                results["keywords"] = keywords
        
        if 'readability' in analysis_types:
            readability = self.analyze_readability(text)
            if "error" not in readability:
                results["readability"] = readability
        
        logger.info("Text analysis completed")
        return results
    
    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """
        Analyze sentiment of text.
        
        Args:
            text: Text to analyze.
            
        Returns:
            A dictionary containing sentiment analysis results.
        """
        logger.info("Analyzing sentiment")
        
        if not text:
            logger.error("No text provided")
            return {"error": "No text provided"}
        
        # Use NLTK's VADER if available
        if self.sentiment_analyzer:
            try:
                scores = self.sentiment_analyzer.polarity_scores(text)
                
                # Determine overall sentiment
                compound = scores['compound']
                if compound >= self.sentiment_threshold:
                    sentiment = "positive"
                elif compound <= -self.sentiment_threshold:
                    sentiment = "negative"
                else:
                    sentiment = "neutral"
                
                return {
                    "sentiment": sentiment,
                    "compound_score": compound,
                    "positive_score": scores['pos'],
                    "negative_score": scores['neg'],
                    "neutral_score": scores['neu']
                }
            except Exception as e:
                logger.warning(f"VADER sentiment analysis failed: {e}")
        
        # Fallback to simple lexicon-based approach
        try:
            # Simple word lists
            positive_words = ["good", "great", "excellent", "amazing", "wonderful", "fantastic", 
                             "terrific", "outstanding", "superb", "brilliant", "awesome", 
                             "happy", "pleased", "satisfied", "love", "like", "enjoy"]
            
            negative_words = ["bad", "terrible", "awful", "horrible", "poor", "disappointing", 
                             "frustrating", "annoying", "unpleasant", "sad", "angry", "hate", 
                             "dislike", "worst", "failure", "failed", "problem"]
            
            # Normalize text
            text_lower = text.lower()
            words = re.findall(r'\b\w+\b', text_lower)
            
            # Count sentiment words
            positive_count = sum(1 for word in words if word in positive_words)
            negative_count = sum(1 for word in words if word in negative_words)
            total_count = len(words)
            
            # Calculate scores
            if total_count > 0:
                positive_score = positive_count / total_count
                negative_score = negative_count / total_count
                neutral_score = 1 - (positive_score + negative_score)
                compound_score = positive_score - negative_score
                
                # Determine overall sentiment
                if compound_score >= self.sentiment_threshold:
                    sentiment = "positive"
                elif compound_score <= -self.sentiment_threshold:
                    sentiment = "negative"
                else:
                    sentiment = "neutral"
                
                return {
                    "sentiment": sentiment,
                    "compound_score": compound_score,
                    "positive_score": positive_score,
                    "negative_score": negative_score,
                    "neutral_score": neutral_score,
                    "note": "Using simple lexicon-based approach"
                }
            else:
                return {
                    "sentiment": "neutral",
                    "compound_score": 0,
                    "positive_score": 0,
                    "negative_score": 0,
                    "neutral_score": 1,
                    "note": "No words found for sentiment analysis"
                }
                
        except Exception as e:
            logger.error(f"Sentiment analysis failed: {e}")
            return {"error": f"Sentiment analysis failed: {e}"}
    
    def extract_entities(self, text: str) -> Dict[str, List[Dict[str, Any]]]:
        """
        Extract named entities from text.
        
        Args:
            text: Text to analyze.
            
        Returns:
            A dictionary mapping entity types to lists of entities.
        """
        logger.info("Extracting entities")
        
        if not text:
            logger.error("No text provided")
            return {"error": "No text provided"}
        
        # Use spaCy if available
        if self.entity_recognizer:
            try:
                doc = self.entity_recognizer(text)
                
                entities = {}
                for ent in doc.ents:
                    entity_type = ent.label_
                    entity_text = ent.text
                    
                    if entity_type not in entities:
                        entities[entity_type] = []
                    
                    # Check if entity already exists
                    if not any(e["text"] == entity_text for e in entities[entity_type]):
                        entities[entity_type].append({
                            "text": entity_text,
                            "start": ent.start_char,
                            "end": ent.end_char
                        })
                
                return entities
            except Exception as e:
                logger.warning(f"spaCy entity extraction failed: {e}")
        
        # Fallback to simple regex-based approach
        try:
            entities = {}
            
            # Extract potential organizations (capitalized multi-word phrases)
            org_pattern = r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)\b'
            orgs = re.findall(org_pattern, text)
            if orgs:
                entities["ORG"] = []
                for org in set(orgs):
                    start = text.find(org)
                    if start >= 0:
                        entities["ORG"].append({
                            "text": org,
                            "start": start,
                            "end": start + len(org)
                        })
            
            # Extract potential people (capitalized names)
            person_pattern = r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\b'
            people = re.findall(person_pattern, text)
            if people:
                entities["PERSON"] = []
                for person in set(people):
                    # Skip if already in organizations
                    if "ORG" in entities and any(person == org["text"] for org in entities["ORG"]):
                        continue
                    
                    start = text.find(person)
                    if start >= 0:
                        entities["PERSON"].append({
                            "text": person,
                            "start": start,
                            "end": start + len(person)
                        })
            
            # Extract dates
            date_pattern = r'\b\d{1,2}[-/]\d{1,2}[-/]\d{2,4}\b|\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},?\s+\d{2,4}\b'
            dates = re.findall(date_pattern, text)
            if dates:
                entities["DATE"] = []
                for date in set(dates):
                    start = text.find(date)
                    if start >= 0:
                        entities["DATE"].append({
                            "text": date,
                            "start": start,
                            "end": start + len(date)
                        })
            
            # Extract numbers
            number_pattern = r'\b\d+(?:\.\d+)?\b'
            numbers = re.findall(number_pattern, text)
            if numbers:
                entities["NUMBER"] = []
                for number in set(numbers):
                    start = text.find(number)
                    if start >= 0:
                        entities["NUMBER"].append({
                            "text": number,
                            "start": start,
                            "end": start + len(number)
                        })
            
            if entities:
                return entities
            else:
                return {"note": "No entities found"}
                
        except Exception as e:
            logger.error(f"Entity extraction failed: {e}")
            return {"error": f"Entity extraction failed: {e}"}
    
    def extract_topics(self, text: str, num_topics: int = None) -> List[Dict[str, Any]]:
        """
        Extract topics from text.
        
        Args:
            text: Text to analyze.
            num_topics: Number of topics to extract. If None, uses default topic_count.
            
        Returns:
            A list of topics with their top words and weights.
        """
        logger.info("Extracting topics")
        
        if not text:
            logger.error("No text provided")
            return {"error": "No text provided"}
        
        if len(text) < 500:
            logger.warning("Text too short for reliable topic modeling")
            return {"warning": "Text too short for reliable topic modeling"}
        
        # Set number of topics
        if num_topics is None:
            num_topics = self.topic_count
        
        # Use gensim if available
        if self.topic_modeler_available:
            try:
                import gensim
                from gensim import corpora
                from gensim.utils import simple_preprocess
                from gensim.parsing.preprocessing import STOPWORDS
                import nltk
                from nltk.stem import WordNetLemmatizer
                
                # Preprocess text
                def preprocess(text):
                    result = []
                    for token in simple_preprocess(text):
                        if token not in STOPWORDS and len(token) > 3:
                            result.append(lemmatizer.lemmatize(token))
                    return result
                
                lemmatizer = WordNetLemmatizer()
                
                # Split text into sentences
                sentences = nltk.sent_tokenize(text)
                processed_sentences = [preprocess(sentence) for sentence in sentences]
                
                # Create dictionary and corpus
                dictionary = corpora.Dictionary(processed_sentences)
                corpus = [dictionary.doc2bow(sentence) for sentence in processed_sentences]
                
                # Train LDA model
                lda_model = gensim.models.LdaModel(
                    corpus=corpus,
                    id2word=dictionary,
                    num_topics=num_topics,
                    passes=10,
                    alpha='auto',
                    per_word_topics=True
                )
                
                # Extract topics
                topics = []
                for topic_id, topic in lda_model.print_topics():
                    # Parse topic string to extract words and weights
                    words_weights = re.findall(r'"([^"]+)"\*(\d+\.\d+)', topic)
                    
                    topic_words = []
                    for word, weight in words_weights:
                        topic_words.append({
                            "word": word,
                            "weight": float(weight)
                        })
                    
                    topics.append({
                        "id": topic_id,
                        "words": topic_words
                    })
                
                return topics
                
            except Exception as e:
                logger.warning(f"Gensim topic modeling failed: {e}")
        
        # Fallback to simple word frequency approach
        try:
            import nltk
            from nltk.corpus import stopwords
            from nltk.tokenize import word_tokenize
            from collections import Counter
            
            # Tokenize and clean text
            stop_words = set(stopwords.words('english'))
            tokens = word_tokenize(text.lower())
            filtered_tokens = [token for token in tokens if token.isalpha() and token not in stop_words and len(token) > 3]
            
            # Count word frequencies
            word_counts = Counter(filtered_tokens)
            
            # Group words into topics (simple clustering by frequency)
            topics = []
            remaining_words = dict(word_counts.most_common(50))  # Top 50 words
            
            for i in range(min(num_topics, len(remaining_words) // 5)):
                # Take top 5 remaining words for this topic
                topic_words = []
                for j in range(5):
                    if remaining_words:
                        word, count = max(remaining_words.items(), key=lambda x: x[1])
                        topic_words.append({
                            "word": word,
                            "weight": count / len(filtered_tokens)
                        })
                        del remaining_words[word]
                
                topics.append({
                    "id": i,
                    "words": topic_words,
                    "note": "Using simple word frequency approach"
                })
            
            return topics
            
        except Exception as e:
            logger.error(f"Topic extraction failed: {e}")
            return {"error": f"Topic extraction failed: {e}"}
    
    def generate_summary(self, text: str, max_length: int = None) -> Dict[str, Any]:
        """
        Generate a summary of text.
        
        Args:
            text: Text to summarize.
            max_length: Maximum length of summary in characters. If None, uses default max_summary_length.
            
        Returns:
            A dictionary containing the summary and metadata.
        """
        logger.info("Generating summary")
        
        if not text:
            logger.error("No text provided")
            return {"error": "No text provided"}
        
        if len(text) < 500:
            logger.warning("Text too short for summarization")
            return {"summary": text, "note": "Text too short for summarization"}
        
        # Set maximum summary length
        if max_length is None:
            max_length = self.max_summary_length
        
        try:
            import nltk
            from nltk.corpus import stopwords
            from nltk.tokenize import sent_tokenize, word_tokenize
            from nltk.probability import FreqDist
            
            # Tokenize text into sentences
            sentences = sent_tokenize(text)
            
            # Tokenize words and remove stopwords
            stop_words = set(stopwords.words('english'))
            word_tokens = word_tokenize(text.lower())
            filtered_words = [word for word in word_tokens if word.isalpha() and word not in stop_words]
            
            # Calculate word frequencies
            word_freq = FreqDist(filtered_words)
            
            # Calculate sentence scores based on word frequencies
            sentence_scores = {}
            for i, sentence in enumerate(sentences):
                sentence_words = word_tokenize(sentence.lower())
                sentence_words = [word for word in sentence_words if word.isalpha() and word not in stop_words]
                
                if len(sentence_words) > 0:
                    score = sum(word_freq[word] for word in sentence_words) / len(sentence_words)
                    sentence_scores[i] = score
            
            # Select top sentences
            num_sentences = max(1, min(len(sentences) // 3, 5))  # At most 1/3 of original sentences, max 5
            top_sentences = sorted(sentence_scores.items(), key=lambda x: x[1], reverse=True)[:num_sentences]
            top_sentences = sorted(top_sentences, key=lambda x: x[0])  # Sort by original order
            
            # Combine sentences into summary
            summary_sentences = [sentences[i] for i, _ in top_sentences]
            summary = ' '.join(summary_sentences)
            
            # Truncate if necessary
            if len(summary) > max_length:
                summary = summary[:max_length].rsplit(' ', 1)[0] + '...'
            
            return {
                "summary": summary,
                "original_length": len(text),
                "summary_length": len(summary),
                "compression_ratio": len(summary) / len(text),
                "sentence_count": len(summary_sentences)
            }
            
        except Exception as e:
            logger.error(f"Summary generation failed: {e}")
            return {"error": f"Summary generation failed: {e}"}
    
    def extract_keywords(self, text: str, num_keywords: int = 10) -> List[Dict[str, Any]]:
        """
        Extract keywords from text.
        
        Args:
            text: Text to analyze.
            num_keywords: Number of keywords to extract.
            
        Returns:
            A list of keywords with their scores.
        """
        logger.info("Extracting keywords")
        
        if not text:
            logger.error("No text provided")
            return {"error": "No text provided"}
        
        try:
            import nltk
            from nltk.corpus import stopwords
            from nltk.tokenize import word_tokenize
            from nltk.probability import FreqDist
            from collections import Counter
            
            # Tokenize and clean text
            stop_words = set(stopwords.words('english'))
            tokens = word_tokenize(text.lower())
            filtered_tokens = [token for token in tokens if token.isalpha() and token not in stop_words and len(token) > 3]
            
            # Count word frequencies
            word_counts = Counter(filtered_tokens)
            
            # Extract keywords
            keywords = []
            for word, count in word_counts.most_common(num_keywords):
                keywords.append({
                    "keyword": word,
                    "score": count / len(filtered_tokens),
                    "count": count
                })
            
            return keywords
            
        except Exception as e:
            logger.error(f"Keyword extraction failed: {e}")
            return {"error": f"Keyword extraction failed: {e}"}
    
    def analyze_readability(self, text: str) -> Dict[str, Any]:
        """
        Analyze readability of text.
        
        Args:
            text: Text to analyze.
            
        Returns:
            A dictionary containing readability metrics.
        """
        logger.info("Analyzing readability")
        
        if not text:
            logger.error("No text provided")
            return {"error": "No text provided"}
        
        try:
            import nltk
            from nltk.tokenize import sent_tokenize, word_tokenize
            
            # Tokenize text
            sentences = sent_tokenize(text)
            words = word_tokenize(text)
            
            # Filter out punctuation
            words = [word for word in words if word.isalpha()]
            
            # Calculate basic metrics
            num_sentences = len(sentences)
            num_words = len(words)
            num_chars = len(''.join(words))
            
            if num_sentences == 0 or num_words == 0:
                return {"error": "Text contains no sentences or words"}
            
            # Calculate average sentence length
            avg_sentence_length = num_words / num_sentences
            
            # Calculate average word length
            avg_word_length = num_chars / num_words
            
            # Calculate syllable count (approximate)
            def count_syllables(word):
                word = word.lower()
                if len(word) <= 3:
                    return 1
                
                # Count vowel groups
                count = 0
                vowels = "aeiouy"
                prev_is_vowel = False
                
                for char in word:
                    is_vowel = char in vowels
                    if is_vowel and not prev_is_vowel:
                        count += 1
                    prev_is_vowel = is_vowel
                
                # Adjust for common patterns
                if word.endswith('e'):
                    count -= 1
                if word.endswith('le') and len(word) > 2 and word[-3] not in vowels:
                    count += 1
                if count == 0:
                    count = 1
                
                return count
            
            syllable_count = sum(count_syllables(word) for word in words)
            avg_syllables_per_word = syllable_count / num_words
            
            # Calculate complex words (words with 3+ syllables)
            complex_words = sum(1 for word in words if count_syllables(word) >= 3)
            percent_complex_words = complex_words / num_words
            
            # Calculate Flesch Reading Ease
            # 206.835 - 1.015 * (words / sentences) - 84.6 * (syllables / words)
            flesch_reading_ease = 206.835 - 1.015 * avg_sentence_length - 84.6 * avg_syllables_per_word
            
            # Calculate Flesch-Kincaid Grade Level
            # 0.39 * (words / sentences) + 11.8 * (syllables / words) - 15.59
            flesch_kincaid_grade = 0.39 * avg_sentence_length + 11.8 * avg_syllables_per_word - 15.59
            
            # Calculate Gunning Fog Index
            # 0.4 * ((words / sentences) + 100 * (complex_words / words))
            gunning_fog = 0.4 * (avg_sentence_length + 100 * percent_complex_words)
            
            # Interpret Flesch Reading Ease
            if flesch_reading_ease >= 90:
                readability_level = "Very Easy"
                grade_level = "5th grade"
            elif flesch_reading_ease >= 80:
                readability_level = "Easy"
                grade_level = "6th grade"
            elif flesch_reading_ease >= 70:
                readability_level = "Fairly Easy"
                grade_level = "7th grade"
            elif flesch_reading_ease >= 60:
                readability_level = "Standard"
                grade_level = "8th-9th grade"
            elif flesch_reading_ease >= 50:
                readability_level = "Fairly Difficult"
                grade_level = "10th-12th grade"
            elif flesch_reading_ease >= 30:
                readability_level = "Difficult"
                grade_level = "College"
            else:
                readability_level = "Very Difficult"
                grade_level = "College Graduate"
            
            return {
                "flesch_reading_ease": flesch_reading_ease,
                "flesch_kincaid_grade": flesch_kincaid_grade,
                "gunning_fog_index": gunning_fog,
                "readability_level": readability_level,
                "grade_level": grade_level,
                "avg_sentence_length": avg_sentence_length,
                "avg_word_length": avg_word_length,
                "avg_syllables_per_word": avg_syllables_per_word,
                "percent_complex_words": percent_complex_words * 100
            }
            
        except Exception as e:
            logger.error(f"Readability analysis failed: {e}")
            return {"error": f"Readability analysis failed: {e}"}
    
    def analyze_text_collection(self, texts: List[str], analysis_types: List[str] = None) -> Dict[str, Any]:
        """
        Analyze a collection of texts and provide aggregate insights.
        
        Args:
            texts: List of texts to analyze.
            analysis_types: List of analysis types to perform. If None, performs all available analyses.
            
        Returns:
            A dictionary containing aggregate analysis results.
        """
        logger.info(f"Analyzing collection of {len(texts)} texts")
        
        if not texts:
            logger.error("No texts provided")
            return {"error": "No texts provided"}
        
        # Set default analysis types if not provided
        if analysis_types is None:
            analysis_types = ['sentiment', 'entities', 'keywords', 'readability']
            
            # Add topics if collection is large enough
            if len(''.join(texts)) > 1000:
                analysis_types.append('topics')
        
        # Analyze individual texts
        individual_analyses = []
        for i, text in enumerate(texts):
            analysis = self.analyze_text(text, analysis_types)
            if "error" not in analysis:
                analysis["text_index"] = i
                individual_analyses.append(analysis)
        
        # Aggregate results
        aggregate_results = {
            "text_count": len(individual_analyses),
            "total_word_count": sum(a.get("word_count", 0) for a in individual_analyses)
        }
        
        # Aggregate sentiment
        if 'sentiment' in analysis_types:
            sentiment_counts = {"positive": 0, "negative": 0, "neutral": 0}
            sentiment_scores = []
            
            for analysis in individual_analyses:
                if "sentiment" in analysis and "sentiment" in analysis["sentiment"]:
                    sentiment = analysis["sentiment"]["sentiment"]
                    sentiment_counts[sentiment] += 1
                    
                    if "compound_score" in analysis["sentiment"]:
                        sentiment_scores.append(analysis["sentiment"]["compound_score"])
            
            if sentiment_scores:
                aggregate_results["sentiment"] = {
                    "distribution": sentiment_counts,
                    "average_score": sum(sentiment_scores) / len(sentiment_scores),
                    "sentiment_variance": np.var(sentiment_scores) if len(sentiment_scores) > 1 else 0
                }
        
        # Aggregate entities
        if 'entities' in analysis_types:
            all_entities = {}
            
            for analysis in individual_analyses:
                if "entities" in analysis and isinstance(analysis["entities"], dict):
                    for entity_type, entities in analysis["entities"].items():
                        if entity_type not in all_entities:
                            all_entities[entity_type] = []
                        
                        for entity in entities:
                            # Check if entity already exists
                            entity_text = entity["text"]
                            existing = next((e for e in all_entities[entity_type] if e["text"] == entity_text), None)
                            
                            if existing:
                                existing["count"] += 1
                            else:
                                entity_copy = entity.copy()
                                entity_copy["count"] = 1
                                all_entities[entity_type].append(entity_copy)
            
            # Sort entities by count
            for entity_type in all_entities:
                all_entities[entity_type].sort(key=lambda x: x["count"], reverse=True)
            
            aggregate_results["entities"] = all_entities
        
        # Aggregate keywords
        if 'keywords' in analysis_types:
            all_keywords = {}
            
            for analysis in individual_analyses:
                if "keywords" in analysis and isinstance(analysis["keywords"], list):
                    for keyword in analysis["keywords"]:
                        keyword_text = keyword["keyword"]
                        
                        if keyword_text in all_keywords:
                            all_keywords[keyword_text]["count"] += keyword.get("count", 1)
                            all_keywords[keyword_text]["documents"] += 1
                        else:
                            all_keywords[keyword_text] = {
                                "keyword": keyword_text,
                                "count": keyword.get("count", 1),
                                "documents": 1
                            }
            
            # Calculate TF-IDF scores
            num_docs = len(individual_analyses)
            for keyword, data in all_keywords.items():
                # Term frequency across all documents
                tf = data["count"] / aggregate_results["total_word_count"]
                # Inverse document frequency
                idf = np.log(num_docs / data["documents"])
                # TF-IDF score
                data["tfidf"] = tf * idf
            
            # Convert to list and sort by TF-IDF
            keywords_list = list(all_keywords.values())
            keywords_list.sort(key=lambda x: x["tfidf"], reverse=True)
            
            aggregate_results["keywords"] = keywords_list[:20]  # Top 20 keywords
        
        # Aggregate readability
        if 'readability' in analysis_types:
            readability_metrics = {
                "flesch_reading_ease": [],
                "flesch_kincaid_grade": [],
                "gunning_fog_index": [],
                "avg_sentence_length": [],
                "avg_word_length": [],
                "avg_syllables_per_word": []
            }
            
            for analysis in individual_analyses:
                if "readability" in analysis and isinstance(analysis["readability"], dict):
                    for metric in readability_metrics:
                        if metric in analysis["readability"]:
                            readability_metrics[metric].append(analysis["readability"][metric])
            
            # Calculate averages
            readability_averages = {}
            for metric, values in readability_metrics.items():
                if values:
                    readability_averages[metric] = sum(values) / len(values)
            
            # Interpret average Flesch Reading Ease
            if "flesch_reading_ease" in readability_averages:
                flesch = readability_averages["flesch_reading_ease"]
                
                if flesch >= 90:
                    readability_level = "Very Easy"
                    grade_level = "5th grade"
                elif flesch >= 80:
                    readability_level = "Easy"
                    grade_level = "6th grade"
                elif flesch >= 70:
                    readability_level = "Fairly Easy"
                    grade_level = "7th grade"
                elif flesch >= 60:
                    readability_level = "Standard"
                    grade_level = "8th-9th grade"
                elif flesch >= 50:
                    readability_level = "Fairly Difficult"
                    grade_level = "10th-12th grade"
                elif flesch >= 30:
                    readability_level = "Difficult"
                    grade_level = "College"
                else:
                    readability_level = "Very Difficult"
                    grade_level = "College Graduate"
                
                readability_averages["readability_level"] = readability_level
                readability_averages["grade_level"] = grade_level
            
            aggregate_results["readability"] = readability_averages
        
        # Extract topics from combined text
        if 'topics' in analysis_types:
            combined_text = ' '.join(texts)
            topics = self.extract_topics(combined_text)
            if "error" not in topics:
                aggregate_results["topics"] = topics
        
        logger.info("Text collection analysis completed")
        return aggregate_results
    
    def analyze_sentiment_trends(self, texts: List[str], timestamps: List[Any]) -> Dict[str, Any]:
        """
        Analyze sentiment trends over time.
        
        Args:
            texts: List of texts to analyze.
            timestamps: List of timestamps corresponding to texts.
            
        Returns:
            A dictionary containing sentiment trend analysis.
        """
        logger.info(f"Analyzing sentiment trends for {len(texts)} texts")
        
        if not texts or not timestamps:
            logger.error("No texts or timestamps provided")
            return {"error": "No texts or timestamps provided"}
        
        if len(texts) != len(timestamps):
            logger.error("Number of texts and timestamps must match")
            return {"error": "Number of texts and timestamps must match"}
        
        # Analyze sentiment for each text
        sentiments = []
        for text in texts:
            sentiment = self.analyze_sentiment(text)
            if "error" not in sentiment:
                sentiments.append(sentiment)
            else:
                sentiments.append({"sentiment": "neutral", "compound_score": 0})
        
        # Convert timestamps to datetime objects if they're not already
        datetime_timestamps = []
        for ts in timestamps:
            if isinstance(ts, datetime):
                datetime_timestamps.append(ts)
            else:
                try:
                    dt = pd.to_datetime(ts)
                    datetime_timestamps.append(dt)
                except:
                    logger.error(f"Could not convert timestamp {ts} to datetime")
                    return {"error": f"Could not convert timestamp {ts} to datetime"}
        
        # Create DataFrame with timestamps and sentiment scores
        data = {
            "timestamp": datetime_timestamps,
            "sentiment": [s["sentiment"] for s in sentiments],
            "compound_score": [s["compound_score"] for s in sentiments]
        }
        df = pd.DataFrame(data)
        
        # Sort by timestamp
        df = df.sort_values("timestamp")
        
        # Resample by day and calculate average sentiment
        df["date"] = df["timestamp"].dt.date
        daily_sentiment = df.groupby("date")["compound_score"].mean().reset_index()
        
        # Calculate rolling average (7-day window)
        if len(daily_sentiment) >= 7:
            daily_sentiment["rolling_avg"] = daily_sentiment["compound_score"].rolling(window=7).mean()
        
        # Calculate overall trend
        if len(daily_sentiment) >= 2:
            x = np.arange(len(daily_sentiment))
            y = daily_sentiment["compound_score"].values
            
            # Linear regression
            slope, intercept = np.polyfit(x, y, 1)
            
            trend_direction = "improving" if slope > 0.01 else "declining" if slope < -0.01 else "stable"
            trend_strength = abs(slope) * 100  # Scale for readability
        else:
            trend_direction = "insufficient data"
            trend_strength = 0
            slope = 0
            intercept = 0
        
        # Prepare result
        result = {
            "overall_trend": {
                "direction": trend_direction,
                "strength": trend_strength,
                "slope": slope
            },
            "daily_sentiment": [
                {
                    "date": row["date"].strftime("%Y-%m-%d"),
                    "sentiment_score": row["compound_score"],
                    "rolling_avg": row.get("rolling_avg")
                }
                for _, row in daily_sentiment.iterrows()
            ]
        }
        
        # Add sentiment distribution
        sentiment_counts = df["sentiment"].value_counts().to_dict()
        result["sentiment_distribution"] = sentiment_counts
        
        # Add notable changes
        if len(daily_sentiment) >= 3:
            daily_changes = daily_sentiment["compound_score"].diff().abs()
            significant_changes = daily_sentiment[daily_changes > daily_changes.mean() + daily_changes.std()]
            
            if not significant_changes.empty:
                result["notable_changes"] = [
                    {
                        "date": row["date"].strftime("%Y-%m-%d"),
                        "sentiment_score": row["compound_score"],
                        "change": row["compound_score"] - daily_sentiment.loc[i-1, "compound_score"] if i > 0 else 0
                    }
                    for i, (_, row) in enumerate(significant_changes.iterrows())
                ]
        
        logger.info("Sentiment trend analysis completed")
        return result
    
    def generate_text(self, prompt: str, max_length: int = 500, temperature: float = 0.7) -> Dict[str, Any]:
        """
        Generate text based on a prompt.
        
        Args:
            prompt: Text prompt to generate from.
            max_length: Maximum length of generated text.
            temperature: Controls randomness (0.0-1.0).
            
        Returns:
            A dictionary containing the generated text.
        """
        logger.info(f"Generating text from prompt: {prompt[:50]}...")
        
        if not prompt:
            logger.error("No prompt provided")
            return {"error": "No prompt provided"}
        
        # Simple Markov chain text generation
        try:
            import nltk
            from nltk.tokenize import word_tokenize
            import random
            
            # Tokenize prompt
            tokens = word_tokenize(prompt.lower())
            
            if len(tokens) < 3:
                logger.warning("Prompt too short for Markov chain generation")
                return {"error": "Prompt too short for Markov chain generation"}
            
            # Build Markov chain (order 2)
            markov_dict = {}
            for i in range(len(tokens) - 2):
                key = (tokens[i], tokens[i+1])
                if key in markov_dict:
                    markov_dict[key].append(tokens[i+2])
                else:
                    markov_dict[key] = [tokens[i+2]]
            
            # Generate text
            current_pair = random.choice(list(markov_dict.keys()))
            result = list(current_pair)
            
            for _ in range(max_length):
                if current_pair in markov_dict:
                    # Apply temperature
                    if temperature < 1.0:
                        # Lower temperature = more deterministic
                        # Higher temperature = more random
                        next_words = markov_dict[current_pair]
                        word_counts = {}
                        for word in next_words:
                            if word in word_counts:
                                word_counts[word] += 1
                            else:
                                word_counts[word] = 1
                        
                        # Convert counts to probabilities and apply temperature
                        total_count = sum(word_counts.values())
                        probs = {word: (count/total_count)**(1/temperature) for word, count in word_counts.items()}
                        
                        # Normalize probabilities
                        prob_sum = sum(probs.values())
                        probs = {word: prob/prob_sum for word, prob in probs.items()}
                        
                        # Choose next word based on adjusted probabilities
                        r = random.random()
                        cumulative_prob = 0
                        next_word = next(iter(probs.keys()))  # Default
                        
                        for word, prob in probs.items():
                            cumulative_prob += prob
                            if r <= cumulative_prob:
                                next_word = word
                                break
                    else:
                        # Full randomness
                        next_word = random.choice(markov_dict[current_pair])
                    
                    result.append(next_word)
                    current_pair = (current_pair[1], next_word)
                else:
                    # No continuation found, restart with a new pair
                    current_pair = random.choice(list(markov_dict.keys()))
                    result.append(current_pair[0])
                    result.append(current_pair[1])
            
            # Convert tokens back to text
            generated_text = ' '.join(result)
            
            # Clean up spacing around punctuation
            generated_text = re.sub(r'\s+([.,;:!?)])', r'\1', generated_text)
            generated_text = re.sub(r'(\()\s+', r'\1', generated_text)
            
            # Capitalize first letter and sentences
            generated_text = generated_text.capitalize()
            generated_text = re.sub(r'([.!?])\s+([a-z])', lambda m: m.group(1) + m.group(2).upper(), generated_text)
            
            return {
                "generated_text": generated_text,
                "length": len(generated_text),
                "method": "markov_chain"
            }
            
        except Exception as e:
            logger.error(f"Text generation failed: {e}")
            return {"error": f"Text generation failed: {e}"}
    
    def analyze_document(self, document_path: str, analysis_types: List[str] = None) -> Dict[str, Any]:
        """
        Analyze a document file.
        
        Args:
            document_path: Path to document file.
            analysis_types: List of analysis types to perform. If None, performs all available analyses.
            
        Returns:
            A dictionary containing analysis results.
        """
        logger.info(f"Analyzing document: {document_path}")
        
        if not os.path.exists(document_path):
            logger.error(f"Document not found: {document_path}")
            return {"error": f"Document not found: {document_path}"}
        
        # Extract text from document
        try:
            text = self._extract_text_from_document(document_path)
            
            if not text:
                logger.error(f"Could not extract text from document: {document_path}")
                return {"error": f"Could not extract text from document: {document_path}"}
            
            # Analyze extracted text
            analysis = self.analyze_text(text, analysis_types)
            
            # Add document metadata
            analysis["document"] = {
                "path": document_path,
                "filename": os.path.basename(document_path),
                "size_bytes": os.path.getsize(document_path),
                "last_modified": datetime.fromtimestamp(os.path.getmtime(document_path)).strftime("%Y-%m-%d %H:%M:%S")
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Document analysis failed: {e}")
            return {"error": f"Document analysis failed: {e}"}
    
    def _extract_text_from_document(self, document_path: str) -> str:
        """
        Extract text from a document file.
        
        Args:
            document_path: Path to document file.
            
        Returns:
            Extracted text.
        """
        file_extension = os.path.splitext(document_path)[1].lower()
        
        # Plain text
        if file_extension in ['.txt', '.md', '.csv', '.json']:
            with open(document_path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
        
        # PDF
        elif file_extension == '.pdf':
            try:
                import PyPDF2
                
                with open(document_path, 'rb') as f:
                    pdf_reader = PyPDF2.PdfReader(f)
                    text = ''
                    for page in pdf_reader.pages:
                        text += page.extract_text() + '\n'
                    return text
            except ImportError:
                logger.warning("PyPDF2 not available, trying alternative method")
                try:
                    import subprocess
                    result = subprocess.run(['pdftotext', document_path, '-'], capture_output=True, text=True)
                    return result.stdout
                except:
                    logger.error("Could not extract text from PDF")
                    return ""
        
        # Word document
        elif file_extension in ['.doc', '.docx']:
            try:
                import docx
                
                doc = docx.Document(document_path)
                text = ''
                for para in doc.paragraphs:
                    text += para.text + '\n'
                return text
            except ImportError:
                logger.warning("python-docx not available")
                return ""
        
        # HTML
        elif file_extension in ['.html', '.htm']:
            try:
                from bs4 import BeautifulSoup
                
                with open(document_path, 'r', encoding='utf-8', errors='ignore') as f:
                    soup = BeautifulSoup(f.read(), 'html.parser')
                    return soup.get_text()
            except ImportError:
                logger.warning("BeautifulSoup not available, using simple regex")
                with open(document_path, 'r', encoding='utf-8', errors='ignore') as f:
                    html = f.read()
                    # Remove HTML tags
                    text = re.sub(r'<[^>]+>', ' ', html)
                    # Remove extra whitespace
                    text = re.sub(r'\s+', ' ', text).strip()
                    return text
        
        # Unsupported format
        else:
            logger.warning(f"Unsupported document format: {file_extension}")
            return ""
    
    def analyze(self, data: Union[str, List[str], Dict[str, Any], pd.DataFrame],
               analysis_type: str = "text") -> Dict[str, Any]:
        """
        Perform cognitive analysis based on data type.
        
        Args:
            data: Input data (text, list of texts, or structured data).
            analysis_type: Type of analysis to perform ('text', 'collection', 'sentiment_trends').
            
        Returns:
            A dictionary containing analysis results.
        """
        logger.info(f"Performing cognitive analysis of type: {analysis_type}")
        
        if not data:
            logger.error("No data provided")
            return {"error": "No data provided"}
        
        # Text analysis
        if analysis_type == "text":
            if isinstance(data, str):
                return self.analyze_text(data)
            else:
                logger.error("Data must be a string for text analysis")
                return {"error": "Data must be a string for text analysis"}
        
        # Collection analysis
        elif analysis_type == "collection":
            if isinstance(data, list) and all(isinstance(item, str) for item in data):
                return self.analyze_text_collection(data)
            else:
                logger.error("Data must be a list of strings for collection analysis")
                return {"error": "Data must be a list of strings for collection analysis"}
        
        # Sentiment trends analysis
        elif analysis_type == "sentiment_trends":
            if isinstance(data, dict) and "texts" in data and "timestamps" in data:
                return self.analyze_sentiment_trends(data["texts"], data["timestamps"])
            elif isinstance(data, pd.DataFrame) and "text" in data.columns and "timestamp" in data.columns:
                return self.analyze_sentiment_trends(data["text"].tolist(), data["timestamp"].tolist())
            else:
                logger.error("Data must contain texts and timestamps for sentiment trends analysis")
                return {"error": "Data must contain texts and timestamps for sentiment trends analysis"}
        
        # Document analysis
        elif analysis_type == "document":
            if isinstance(data, str) and os.path.exists(data):
                return self.analyze_document(data)
            else:
                logger.error("Data must be a valid file path for document analysis")
                return {"error": "Data must be a valid file path for document analysis"}
        
        # Unsupported analysis type
        else:
            logger.error(f"Unsupported analysis type: {analysis_type}")
            return {"error": f"Unsupported analysis type: {analysis_type}"}
    
    def _ensure_dataframe(self, data: Union[pd.DataFrame, Dict[str, Any], List[Dict[str, Any]]]) -> pd.DataFrame:
        """
        Convert input data to a pandas DataFrame if it's not already.
        
        Args:
            data: Input data as DataFrame or dictionary/list of dictionaries.
            
        Returns:
            A pandas DataFrame.
        """
        if isinstance(data, pd.DataFrame):
            return data
        elif isinstance(data, dict):
            return pd.DataFrame([data])
        elif isinstance(data, list):
            return pd.DataFrame(data)
        else:
            raise ValueError("Data must be a pandas DataFrame, dictionary, or list of dictionaries")
