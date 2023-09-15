# earnings-finBERT-sentiment
This project tries to calculate a relationship between sentiment of earnings calls and returns of a company's stock. From this project, we come to the conclusion that there is no relationship between forward returns and earning call sentiment, but there is a relationship between backward returns and sentiment.

A report summarizing our findings and the methods we used in this project is in report.pdf. A code appendix is also attached to the back of that report.

A raw version of the appendix is also included in the /code directory, saved as appendix-and-R-analysis.Rmd. That directory also contains the following files:

download-calls.py -  This file scrapes earnings call transcripts from the Motley Fool website. If you want to replicate this, make sure to make an empty folder called 'out-text-analysis' within the code directory to start all of the transcripts.

finBERT-and-configuration.py - This file creates the dataframe that is used for our analysis in R. It iterates through each transcript to calculate the sentiment using finBERT, and then combines it together with other metadata, such as company sector, beta, and returns in the month prior and month after. In order to run this file, you need an API key for Alpaca (https://alpaca.markets/)
