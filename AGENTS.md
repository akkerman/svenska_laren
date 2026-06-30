# Svenska Lären - AI-Powered Swedish Learning Agent

Svenska Lären is an intelligent language learning application designed to help users master Swedish through personalized, adaptive learning techniques powered by AI.

## Project Overview

Svenska Lären combines modern AI technology with proven language learning methodologies to create an interactive and effective Swedish learning environment. The application features three core learning modules - flashcards with spaced repetition, translation exercises, and conversation practice - all tailored to the user's proficiency level.

## Key Features

### 1. Spaced Repetition System (Leitner Box)
- **5-box adaptive review system** for optimal memory retention
- **Smart scheduling** based on learning progress and difficulty settings
- **Progress tracking** with detailed statistics per learning box
- **Frequency-based vocabulary filtering** that adjusts to user's skill level

### 2. Interactive Translation Exercises
- **Bidirectional translation** between Swedish and Dutch
- **Context-aware sentence generation** powered by local Ollama AI
- **Intelligent feedback system** that identifies errors and provides corrections
- **Topic-specific content** for focused practice sessions

### 3. Real-time Conversations
- **Natural language conversation** with AI Swedish partner
- **Adaptive difficulty responses** that match user's skill level
- **Integrated correction system** providing grammar feedback during conversations
- **Streamed responses** using Server-Sent Events for smooth interaction

## Technical Architecture

### Backend (Python/FastAPI)
- **Database**: SQLite with SQLAlchemy ORM
- **AI Integration**: Local Ollama instance running the `alibayram/erurollm-9b-instruct` model
- **API Endpoints**:
  - `/api/cards` - Flashcard management and spaced repetition
  - `/api/translation` - Translation exercises with AI generators
  - `/api/conversation` - Real-time conversation system
  - `/api/settings` - User difficulty adjustment

### Frontend (React/Vite)
- **Responsive Design** for desktop and mobile users
- **Real-time Communication** with backend APIs
- **Interactive Learning Components** for all modules
- **Settings Management** with difficulty slider

## Learning Methodology

The app employs a **personalized adaptive learning approach** where difficulty automatically adjusts based on the user's performance, creating an optimal learning experience. The system features:

1. **Adaptive Vocabulary Selection**: Based on difficulty level and frequency ranking
2. **Progressive Complexity**: Sentences and conversations adjust in complexity with user advancement
3. **Spaced Repetition**: Review intervals increase as knowledge improves
4. **Intelligent Assessment**: Real-time feedback for translation and conversation practice

## AI Integration Details

The application utilizes a local Ollama instance to provide:
- **Text Generation** for translation exercises and conversation topics
- **Natural Language Processing** for feedback analysis and correction
- **Context-Aware Responses** in Swedish learning exercises

## Usage Scenarios

### For Beginners (Difficulty 0.0-0.3)
- Simple vocabulary, basic sentences
- Frequent English translations for clarity
- Foundation building through repetition

### For Intermediate Learners (Difficulty 0.3-0.6)
- Mixed tenses and sentence structures
- Broader vocabulary range
- Conversational practice with moderate complexity

### For Advanced Learners (Difficulty 0.6-1.0)
- Complex grammar and idiomatic expressions
- Native-level conversation practice
- Comprehensive error correction and feedback

## Setup Requirements

1. **Ollama**: Run with `alibayram/erurollm-9b-instruct` model
2. **Python 3.9+**: For backend with pipenv setup
3. **Node.js 18+**: For frontend with npm packages

## Target Audience

Svenska Lären is designed for:
- Language learners at all levels seeking structured Swedish practice
- Users wanting to improve Swedish speaking and translation skills
- Individuals looking for personalized, AI-powered language learning
- Learners who prefer self-paced study using local AI resources

The application combines academic research on spaced repetition with modern AI capabilities to create an effective, personalized language learning experience.