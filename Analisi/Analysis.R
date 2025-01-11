# ------------------------------- INIT ----------------------------------
#Loading library
library(igraph)
library(ggplot2)
library(plyr)
#Function necessary for creation of triangle shape
mytriangle <- function(coords, v=NULL, params) {
  vertex.color <- params("vertex", "color")
  if (length(vertex.color) != 1 && !is.null(v)) {
    vertex.color <- vertex.color[v]
  }
  vertex.size <- 1/200 * params("vertex", "size")
  if (length(vertex.size) != 1 && !is.null(v)) {
    vertex.size <- vertex.size[v]
  }
  
  symbols(x=coords[,1], y=coords[,2], bg=vertex.color,
          stars=cbind(vertex.size, vertex.size, vertex.size),
          add=TRUE, inches=FALSE)
}
# clips as a circle
add_shape("triangle", clip=shapes("circle")$clip,
          plot=mytriangle)

#loading data
timeline <- read.csv("Timeline.csv")
conversation <- read.csv("Conversation.csv")
tweets <- read.csv("Tweets.csv")
selected_tweets <- read.csv("SelectedTweets.csv")

count(tweets, "text")
nrow(timeline)
nrow(conversation)
nrow(tweets)
nrow(selected_tweets)
#merging data
conversation = merge(x = conversation, y = selected_tweets, by = "conversation_id", all.x = TRUE)
conversation$conversation_id <- NULL
conversation$id <- NULL
conversation$public_metrics <- NULL


# ------------------------------- PLOT ----------------------------------
#Polarization
ggplot(timeline, aes(x = polarization)) + 
  geom_density(fill="orange", alpha=0.8) + 
  scale_x_continuous(limits = c(-1,1), 
                     breaks=c(-1,1),
                     labels=c("Cons","Pros")) +
  labs(x = "polarization", y = "PDF", title = "Polarization of Twitter user (GREEN PASS)") +
  theme_bw()

#Count of tweets sentiment
ggplot(data = tweets) + 
  geom_bar(mapping = aes(x = text, fill = text), alpha = 0.8) +
  labs(x = "Sentiment", y = "Count of tweets", title = "Sentiment of lasth month tweets", fill = "Sentiment") + 
  scale_fill_manual(labels = c("Negative", "Positive"), values = c("dark red", "dark green")) +
  scale_x_discrete(labels= c("Negative", "Positive"))

#Public metrics of last month tweets
ggplot(data = tweets, aes(x = text, y=public_metrics, fill = text)) + 
  geom_bar(stat = "identity", alpha = 0.8) +
  labs(x = "Last month tweets", y = "Public metrics", title = "public metrics of the lasth month tweet", fill = "Sentiment") + 
  scale_fill_manual(labels = c("Negative", "Positive"), values = c("dark red", "dark green")) +
  scale_x_discrete(labels= c("Negative", "Positive"))
  
#Public metrics of the 10 selected tweets
ggplot(data = selected_tweets, aes(x = as.character(conversation_id), y=public_metrics, fill = text)) + 
  geom_bar(stat = "identity", alpha = 0.8) +
  labs(x = "Last month tweets", y = "Public metrics", title = "public metrics of the lasth month tweet", fill = "Sentiment") + 
  scale_fill_manual(labels = c("Negative", "Positive"), values = c("dark red", "dark green"))+ 
  scale_x_discrete(labels= c(1,2,3,4,5,6,7,8,9,10))

# ------------------------------- GRAPH ----------------------------------
#Graph creation
net <- graph_from_data_frame(d=conversation, directed=T)
net <- simplify(net, remove.multiple = F, remove.loops = T)

#Attributes
V(net)$frame.color <- "black"
V(net)$label <- ""

#Edge color and form depends on conversation
ecol <- rep("dark green", ecount(net))
ecol[E(net)$text=="['negative']"] <- "dark red"
E(net)$color = ecol
elty <- rep(1, ecount(net))
elty[E(net)$text=="['negative']"] <- 2
E(net)$lty = elty

#polarization needed to color and size of the vertexes
vpol <- rep(0, vcount(net))
vpol[V(net)$name%in%timeline$id] <- timeline$polarization

vcol <- rep("black", vcount(net))
vcol[vpol < 0] <- "dark red"
vcol[vpol > 0] <- "dark green"
V(net)$color <- vcol

vsha <- rep("triangle", vcount(net))
vsha[vpol < 0] <- "circle"
vsha[vpol > 0] <- "square"
V(net)$shape <- vsha

vpol[vpol < 0] <- vpol[vpol < 0]*-1
vpol[vpol == 0] <- vpol[vpol == 0]+1
V(net)$size <- vpol*4

#Displaying the graphs
l1 <- layout.fruchterman.reingold(net)
plot(net, layout=l1, edge.arrow.mode=0, main="Green Pass Social Interaction on Twitter")
legend('topleft',legend=c("Positive", "Negative", "Neutral"), pch=c(15,16,17), pt.cex=1.5, col=c('dark green', 'dark red', 'black'))
legend('topright',legend=c("Positive conversation", "Negative conversation"), lty=c(1,2), col=c('dark green', 'dark red'))

#getting giant component
cl <- clusters(net)
net <- induced.subgraph(net, which(cl$membership == which.max(cl$csize)))

#Displaying the giant component graphs
l1 <- layout.fruchterman.reingold(net)
plot(net, layout=l1, edge.arrow.mode=0, main="Green Pass Social Interaction on Twitter")
legend('topleft',legend=c("Positive", "Negative", "Neutral"), pch=c(15,16,17), pt.cex=1.5, col=c('dark green', 'dark red', 'black'))
legend('bottomleft',legend=c("Positive conversation", "Negative conversation"), lty=c(1,2), col=c('dark green', 'dark red'))

