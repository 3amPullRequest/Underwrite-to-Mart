# About

This is my personal Capstone Project where I attempt to tackle a common problem in the Actuarial industry: extracting data from messy sources. My core idea is as follows, expressed via the ETL Framework.

### Extract

Retrieval Augmented Generation (RAG) to extract a comprehensive summary of the requested data from Word Documents$^1$. Use metadata filtering, followed by a hybrid keyword, semantic and agentic search. The keyword and semantic search can locate the relevant location of the data, and the agentic search can help with picking up relevant footnotes that otherwise would not have been noticed.

### Transform

An agent looks at the extracted data, and determines if it requires any judgement. If it does, it flags it for human review (human-in-the-loop). Otherwise, it attempts to populate the relevant Data Mart's strictly defined schema (generic and business-logic validation). If it is unable to populate it, it tries again a maximum of 10 times-- attempts exceeding that flags it for human review.

### Load
The model points will be loaded into their respective Data Mart for use by the relevant department (I am doing it for Actuarial).

### Analyse
Now, with the data nice and clean, we can perform our analysis. This project will use a GLM as an example.

# Introduction

### The Problem


Traditionally, when faced with data strewn everywhere (benchmarks littered in workpaper Excel files, property specifications in unstructured webpages, medical claims history in PDFs, etc...), a poor intern (not me fortunately) or a poor junior will be assigned to extract the data by hand.

I have identified three major reasons why this is so difficult to automate.

##### 1. Heavily Context-Dependent Data
The numbers don't always tell the full story-- qualitative data is often still of immense importance. So we can't reasonably just ask people to fill in a database directly. In larger companies, I notice that analytics engineers are hired to solve this issue. But getting them to clean up too much might inadvertently strip away crucial context that Actuaries may need.
##### 2. Upstream Users not Bound to a Standard Operating Procedure
Point **1** also contributes heavily to lack of automation. This is not to fault the upstream users. It is simply terribly difficult to create an SoP if the most reasonably efficient method for underwriters to input data ranges from a PDF template to a terribly verbose spreadsheet.
##### 3. Not Enough Data
According to my friends who worked with social media analytics, it isn't uncommon to rely on the Law of Large Numbers to dampen the impact of random errors introduced by the Natural Language processor. But risk professionals, especially Actuaries who don't typically have the luxury of hundreds of millions of data points to dampen anything, need greater rigour. Relatively mild increases in variance can lead to higher Risk Margins (Provision for Adverse Deviation) and regulatory capital requirements, incurring opportunity cost in the millions.

### Why this project can be the solution



# Footnotes

1. PDFs introduce significant complications for LLMs, in that it uses what is called a 'Fixed Coordinate Architecture', where under the hood every element is mapped to a coordinate. This works well and consistent when many different machines view it, but trying to parse it to text will just return gibberish (because it cares only about the physical location of the characters, not about the structure of the document). A common workaround is to use Optical Character Recognition (OCR) to visually parse it to text, but this can be unreliable (eg: 1 vs l vs I??). Therefore, to simplify matters, I elected to start with Word Documents, which is actually just a zipped bunch of XML files organised neatly (Dynamic Flow Architecture).