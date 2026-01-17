# sentiment-playlist-generator-extension
improvements to the original sentiment playlist generator project






why use a distributed system with five different microservices
    why we need:
        gateway - wanted it to act as the source of all truth for other microservices
        ai - needed for when I want to scale or re-train AI model later on
        music - right now all songs in my project are simply all objects in a Songs class. Therefore, I wanted to split
        (also, ai and music most likely to be the main source of errors so need to split them up)
        db - this is necessary, cannot have user-facing servers access the db
        auth - wanted this server to act as the single source of truth for all user authentication

why the addition of celery tasks for async and not just stick with the previous structure
    keeps gateway responsive and open for other connection.
    significantly reduces request response time.

why pubsub listener thread for each gateway with websocket connection per request from frontend
    this is a perfect addition to the celery task.
    Instead of the frontend polling until the task is finished, which can slow down gateway if multiple requests are waiting simultaneously
    We use webscoket with a pubsub listener which is computationally less costly than responding to each polling request

why redis caching
    It has come to my attention that certain emotions are way more common for the majority of users (e.g. sad->happiness, boredom->enthusiasm)
    therefore, it only made sense to use caching for the ai prediction and the playlist generation algorithms.
    My metrics show these two tasks as the main bottleneck for response latency.

why use ALL logging, dlq and metrics count?
    logging is for short-term forensics and debugging for developers (also in suitable format for services like cloudwatch)
    dlq tells us what exactly went wrong WHEN something goes wrong (currently my dlq is purely to be used for mlops later, but can add some sort of logic later on)
    metrics just counts important metrics for our project (e.g. duration ms)
    we combine these two to provide transparency in observation later on.