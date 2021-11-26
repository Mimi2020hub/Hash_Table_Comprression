Hash Table Compression during Query Evaluation

To run the scripts: python ussr.py, python dgps.py

We implement  Gubner et al. (2020)’s paper -- Efficient Query Processing with Optimistically Compressed Hash Tables & Strings in the USSR. This project focuses on the research problem of how to enhance representation of hash tables and the data within them to reduce memory consumption and improve query performance. We follow Gubner et al. (2020)’s hypothesis that shrinking hash tables through three complementary techniques – Domain-Guided Prefix Suppression, Optimistic Splitting and Unique Strings Self-aligned Region will lower memory footprint and increase query evaluation.

We successfully implement the USSR system with the optimistic splitting to enhance the performance of comparisons and other operations by reducing the size of significant hashes. For the USSR system, we implemented four basic functions, insertion, searching, updating, as well as deletion. To achieve the SIMD, we use Python Numpy to simulate the hash table for our USSR system. Besides,  we successfully implement the Domain-Guided Prefix Suppression packing function by following the steps described in the target paper.
