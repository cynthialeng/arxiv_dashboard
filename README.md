# ArXiv Dashboard
A dashboard for displaying arXiv metadata in accessible ways.

# Database Documentation

This database contains processed and derived metadata tables constructed from arXiv submission records. The schema supports longitudinal, author-level, category-level, and topic-based analysis of arXiv publications.

#### 1. `papers2.csv` — Primary Table

This is the central table containing one row per arXiv submission. All downstream tables are derived from this table.

| Column Name      | Data Type | Key Type        | Description                                                         |
| ---------------- | --------- | --------------- | ------------------------------------------------------------------- |
| `id`             | TEXT      | Primary Key     | Unique arXiv identifier for the paper (e.g., `2512.05118`).         |
| `title`          | TEXT      | —               | Title of the paper as submitted to arXiv.                           |
| `abstract`       | TEXT      | —               | Abstract text describing the paper’s content.                       |
| `authors_raw`    | TEXT      | —               | Raw authorship string provided by arXiv.                            |
| `categories`     | TEXT      | —               | Space-delimited list of arXiv category codes assigned to the paper. |
| `submitted_year` | INTEGER   | —               | Year the first version of the paper was submitted.                  |
| `submitted_date` | DATE      | —               | Date the first version of the paper was submitted.                  |
| `doi`            | TEXT      | —               | Digital Object Identifier, if available.                            |
| `journal_ref`    | TEXT      | —               | Information about the journal the paper was published in.           |
| `comments`       | TEXT      | —               | Author-provided comments (e.g., page count, figures).               |

#### 2. `abstract_length_by_year.csv` — Abstract Length Statistics

This table summarizes abstract length trends over time.

| Column Name     | Data Type | Key Type        | Description                                                         |
| --------------- | --------- | --------------- | ------------------------------------------------------------------- |
| `year`          | INTEGER   | Primary Key     | Submission year.                                                    |
| `avg_length`    | FLOAT     | —               | Average abstract word count for papers submitted in the given year. |
| `median_length` | FLOAT     | —               | Median abstract word count for papers submitted in the given year.  |

#### 3. `author_counts.csv` — Author Publication Counts by Year

This table provides a longitudinal author–year panel derived from parsed authorship strings.

| Column Name   | Data Type | Key Type                  | Description                                                      |
| ------------- | --------- | ------------------------- | ---------------------------------------------------------------- |
| `author`      | TEXT      | Primary Key | Normalized author name parsed from `authors_raw`.                |
| `year`        | INTEGER   | Primary Key | Submission year.                                                 |
| `paper_count` | INTEGER   | —           | Number of papers by the given author in the given year. |


#### 4. `category_counts_alltime.csv` — All-Time Category Frequencies

This table summarizes total paper counts by arXiv category code across all years.

| Column Name     | Data Type | Key Type        | Description                                       |
| --------------- | --------- | --------------- | ------------------------------------------------- |
| `category_code` | TEXT      | Primary Key     | arXiv category code (e.g., `cs.LG`).              |
| `count`         | INTEGER   | —               | Total number of papers assigned to this category. |


#### 5. `category_map.csv` — arXiv Category Metadata

This table maps arXiv category codes to human-readable category names.

| Column Name     | Data Type | Key Type        | Description                                                  |
| --------------- | --------- | --------------- | ------------------------------------------------------------ |
| `category_code` | TEXT      | Primary Key     | Official arXiv category code.                                |
| `category_name` | TEXT      | —               | Descriptive category name (e.g., “Artificial Intelligence”). |

#### 6. `default_table.csv` — Recent Paper Metadata (Dashboard View)

This table contains a recent subset of papers for display in the dashboard.

| Column Name  | Data Type | Key Type    | Description                           |
| ------------ | --------- | ----------- | ------------------------------------- |
| `id`         | TEXT      | Primary Key | arXiv paper identifier.               |
| `title`      | TEXT      | —           | Title of the paper.                   |
| `authors`    | TEXT      | —           | Raw authorship string.                |
| `categories` | TEXT      | —           | Space-delimited arXiv category codes. |
| `date`       | DATE      | —           | Submission date.                      |
| `comments`   | TEXT      | —           | Author-provided comments.             |

#### 7. `multicategory_by_year.csv` — Multi-Category Assignment Trends

This table quantifies the prevalence of papers assigned to multiple categories over time.

| Column Name | Data Type | Key Type        | Description                                                           |
| ----------- | --------- | --------------- | --------------------------------------------------------------------- |
| `year`      | INTEGER   | Primary Key     | Submission year.                                                      |
| `sum`       | INTEGER   | —               | Number of papers assigned to more than one category.                  |
| `share`     | FLOAT     | —               | Proportion of papers assigned to more than one category. |

#### 8. `dl.csv`, `ml.csv`, `rl.csv`, `llm.csv`, `homepage.csv` - Topic Trend Tables

These tables share an identical schema and capture annual submission counts for specific topics or overall submissions.

| Column Name | Data Type | Key Type        | Description                                                      |
| ----------- | --------- | --------------- | ---------------------------------------------------------------- |
| `year`      | INTEGER   | Primary Key     | Submission year.                                                 |
| `count`     | INTEGER   | —               | Number of papers matching the topic criteria for the given year. |

**Table purposes:**

* `dl`: Deep Learning–related papers
* `ml`: Machine Learning–related papers
* `rl`: Reinforcement Learning–related papers
* `llm`: Large Language Model–related papers
* `homepage`: Total arXiv submissions per year
