# sentiment-playlist-generator-extension
improvements to the original sentiment playlist generator project. This is over engineered by design to learn system design and real deployment knowledge.

This project explores the intersection of machine learning and music recommendation. It uses sentiment analysis to classify text input from the user into different emotions, and then generates a playlist that the gradually transitions from the detected emotion to the user's emotion of choice.

A dataset of 1,000 songs is mapped onto a 2D Valence–Arousal graph, allowing a graph traversal algorithm to find a smooth emotional path between the starting and target moods.

🧠 Modeling: trained on a labeled dataset of emotions using neural networks.

🎵 Application: maps predicted sentiment → emotion-sensitive playlist generation.

💡 Goal: demonstrate how AI can bridge natural language understanding and personalized music experiences, including potential applications in music therapy.

documentation for the original project: https://docs.google.com/document/d/1xRGxF-19MLz0YQcSxIe7rRYlSt83DojQSZsl5oeYK54/edit?usp=sharing
