# Data Analytics Project:
A multidimensional Nutri-Score for food products based on nutrient density, nutrient distribution and harmfulness.

### The problem:
Nutri-Scores are a popular tool for evaluating the nutritional value of food products. However, there are concerns about their reliability and accuracy. For example, some ultra-processed foods can receive the highest category “A” ranking, despite being high in unhealthy ingredients. Additionally, sweeteners like glucose-fructose syrup and other potentially harmful ingredients like anti-nutrients or heavy metals are not taken into account. Aspects such as added ingredients and their bioavailability are also completely neglected. This can lead to misleading information for consumers who rely on Nutri-Scores to make healthy food choices. To improve the reliability of Nutri-Scores, it may be necessary to consider a wider range of factors and to develop more comprehensive evaluation criteria.

### What I want to achieve:
To address some of these limitations of the current Nutri-Score system, I aim to reevaluate the current rating system and incorporate additional dimensions. This optimized, more reliable Nutriscore does not only assess food based on its macronutrients in the context of the respective food group, but also evaluates each food with a comprehensive, multidimensional point system that takes into account micronutrients, fatty acids, secondary plant substances and other components across all foods. This point system is subdivided into a value for nutrient density by volume, nutrient density by calories, how well the distribution of nutrients covers an average need and how harmful the food can be for humans due to certain components. 
However, this task should not be understood as a quick and easy solution. Instead, it is an ongoing project that keeps improving over time. The results can be used to inform consumers and policymakers about the nutritional quality of food products and to encourage healthier eating habits. Moreover, this project will also provide me with an opportunity to train and improve my skills in data analytics and data science by scraping, cleaning, analyzing, and showcasing the data with visualization tools.

### Working steps:
To achieve the project objectives, I will develop a web crawler using Python to collect nutrient information from reliable open-source web pages. My primary source will be Nährwertrechner.de because it provides detailed information on the nutrient composition of thousands of food products and is easily accessible. The scraped data will be stored in a SQL database and segmented into different tables based on the food value dimensions. From there, I will analyze the data locally and create customized evaluation criteria based on the latest research. The results will be visualized using Tableau or Power BI to provide an intuitive and user-friendly representation of the data. Additionally, I plan to publish the results on a dedicated project website in addition to my GitHub repository.

### Checkmarks regarding the current status
- [x] Create a WebCrawler for Nährwertrechner.de
- [x] Scrape some data about nutritional information
- [x] Store the scraped data in DataFrames and export them to Excel
- [x] Scrape some data about nutritional recommendations (just an average guideline)
- [x] Store the data in SQL (just for the category Vitamins)
- [x] Clean the data (just for the category Vitamins)
- [ ] Calculate the percentage coverage of the requirement for each nutrient
- [ ] Calculate the distribution of nutrient coverage
- [ ] Repeat these steps for every category
...