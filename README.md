# 🐦 Green Pass Sentiment Analysis on Twitter

## Overview  
This project explores public sentiment and social interactions on Twitter regarding the Green Pass and Super Green Pass policies introduced in Italy during 2021. By analyzing tweets from January 2022, the study identifies sentiment polarization, echo chambers, and interactions between opposing groups on this topic.  
![image](https://github.com/user-attachments/assets/68ff5efa-6640-42bf-8ecd-bf99bda12d8b)

## Data Collection Process  
The data collection and processing rely on Twitter APIs and custom scripts. Below are the steps to reproduce the dataset:  

### 🛠️ Instructions  
1. **▶️ Run the Main Script**  
   Execute the `API_twitter_request` script from the command line.  
   - This script will generate the datasets: `tweet`, `selected_tweet`, and `conversation`.  

2. **⚙️ Adjust Parameters**  
   - Observe the number of authors printed by the script.  
   - Input this value into `API_Run_timeline_script` to set the range for `range(0, numero_righe_conversation)`.

3. **⬇️ Download Timeline Data**  
   Run `API_Run_timeline_script` to download timeline datasets incrementally.  
   - The script generates partial files in the format `timeline[init-finish].csv`.  
   - Once completed, the consolidated `timeline.csv` dataset will be created.  
   - The partial files are no longer needed, but they can serve as backups.

4. **📊 Generate Graphs and Analyze Data**  
   Navigate to the `analisi` folder to access the R scripts for visualizing data and creating graphs.  

---

## 🛑 Troubleshooting
- If you encounter errors (e.g., "API connection timed out") or if your system slows down during partial dataset creation:  
  - Reduce the `step` value in `API_Run_timeline_script`.  
  - Decrease the number of tweets downloaded per timeline in `API_timeline.py`.  

- To manually download datasets:  
  Use the following command:  
  ```bash
  python API_timeline.py 100 150
  ```
  This will download tweets for the specified range and create a file timeline[101-150].csv.
  Combine these partial files later by executing the second part of the API_Run_timeline_script.

## 📂 Dataset Description
The datasets created include:

- 📝 Tweet Dataset: Contains all tweets from January 2022 related to the Green Pass (#greenpass, #supergreenpass, in Italian).
- 🔍 Selected Tweets: Top 5 positive and negative tweets based on public engagement metrics (likes, comments, retweets).
- 💬 Conversation Dataset: Contains replies and interactions from users discussing the selected tweets.
- 🕒 Timeline Dataset: Aggregated tweets from user timelines filtered for relevance to the Green Pass topic.

## 📊 Research Insights
The project analyzes:

- Sentiment distribution: Positive vs. Negative tweets.
- Echo chambers: Interaction networks indicating group polarization.
- User polarization: Quantified on a scale from -1 (completely negative) to +1 (completely positive).

## 🧰 Tools and Technologies
- Languages: Python, R
- Libraries:
- Python: Tweepy, Pandas, NumPy
- R: ggplot2, dplyr

## 📫 Contact
For further details, feel free to reach out:

- Author: Andrea Munarin
- 📧 Email: andrea.munarin00@gmail.com
- 🏛️ Affiliation: Ca' Foscari University of Venice, Italy

## 🙌 Acknowledgments
This study is part of ongoing research on social interactions and sentiment analysis, with a focus on the societal impacts of health policies.
