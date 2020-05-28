import tweepy
import langdetect as ld
# authorization tokens
consumer_key = "YNDo3diRMEAdYpFdRwVIOGxZU"
consumer_secret = "87Y1eBTG9UFb9ijEtQBTMXlwqOX0hcpvk2xGpay1m8pXyNnd4X"
access_key = "179873833-efkJgKhYS9rjVdGaGgAMxLU4xW3YAZ2IfKbQkFTl"
access_secret = "p595QnRKdcDytoGe8yBtb3Dp0kRMXpILPT4Y9YJ1FxJqf"


class StreamListener(tweepy.StreamListener):
    def on_status(self, status):
        print(status.id_str)
        is_retweet = hasattr(status, "retweeted_status")

        if hasattr(status,"extended_tweet"):
            text = status.extended_tweet["full_text"]
        else:
            text = status.text

        is_quote = hasattr(status, "quoted_status")
        quoted_text = ""
        if is_quote:
            if hasattr(status.quoted_status,"extended_tweet"):
                quoted_text = status.quoted_status.extended_tweet["full_text"]
            else:
                quoted_text = status.quoted_status.text

        remove_characters = [",","\n"]
        for c in remove_characters:
            text.replace(c," ")
            quoted_text.replace(c, " ")

        with open("corpus.csv", "a", encoding='utf-8') as f:
            f.write("%s\n" % (text))

    def on_error(self, status_code):
        print("Encountered streaming error (", status_code, ")")
        sys.exit()

if __name__ == "__main__":
    # complete authorization and initialize API endpoint
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_key, access_secret)
    api = tweepy.API(auth)

    # initialize stream
    streamListener = StreamListener()
    stream = tweepy.Stream(auth=api.auth, listener=streamListener,tweet_mode='extended')
    with open("corpus.csv", "w", encoding='utf-8') as f:
        f.write("text\n")
        tags = []
        with open("keywords.txt", encoding = 'utf-8') as g:
            tags = g.read().splitlines()
        stream.filter(track=tags, languages = ['ru'])
        

    
