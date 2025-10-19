---
TITLE: Yoga4All
AUTHOR: Priyanka Rajeev Hichkad
---

Yoga4All is a **Ubiquitous Computing project** under the guidance of **Prof. Hari Prabhat Gupta, Department of Computer Science and Engineering, IIT BHU**.  
The project leverages **wearable motion sensors** to recognize yoga poses, focusing initially on *Surya Namaskar (Sun Salutation)*, and aims to provide feedback on correctness and performance analysis.  

---

## Project Overview  
Yoga4All is designed to make yoga practice smarter and more accessible by utilizing **time-series sensor data** rather than vision-based methods. Sensor readings are collected using **MPU-9250 IMU sensors**, which provide **accelerometer, gyroscope, and magnetometer data** stored in CSV format.  

The project objectives are:  
- Detect and classify yoga poses using **machine learning and deep learning sequence models** (LSTM, GRU, and related architectures).  
- Construct a **Directed Acyclic Graph (DAG)** where nodes represent poses and edges represent transition times.  
- Develop **feedback mechanisms** for evaluating execution speed, angular deviation, and overall correctness.  
- Expand the system beyond Surya Namaskar to accommodate broader yoga practices in future work.  

---

## Current Progress  

**Week 1:**  
- Understood the project scope and divided responsibilities among groups.  
- Reviewed the research paper *YogaHelp: Leveraging Motion Sensors for Learning Correct Execution of Yoga with Feedback*.  
- Explored the three types of motion sensors being used; two procured, one designed by our senior.  
- Understood that the sensors record data in **CSV format** containing accelerometer, gyroscope, and magnetometer readings.  
- Learned about the project’s **REST API** (Swagger), which enables data upload and access from remote systems.  

**Week 2:**  
- Initiated **data collection** by performing Surya Namaskar with wrist-mounted sensors, with parallel video recordings for validation.  
- Explored deep learning approaches, particularly **LSTM and GRU**, as suitable models for time-series data.  
- Studied a **Human Activity Recognition (HAR) model** from Kaggle to identify strategies applicable to our dataset.  

**Week 3:**  
- Continued structured data collection (approximately 10 sets weekly, 1 set = 2 Surya Namaskar rounds).  
- Processed data by aligning sensor readings with video-recorded timings, removing unnecessary or noisy segments.  
- Conducted additional data collection at the **Student Activity Centre (SAC)** to capture Surya Namaskar performed with proper form.  

---

## Next Steps  
- **Data Preprocessing:** Develop robust scripts for cleaning, segmentation, and normalization of sensor signals.  
- **Data Labeling:** Finalize an approach to label each data segment with its corresponding yoga pose to enable supervised learning.  
- **Model Development:** Train and compare multiple deep learning models (LSTM, GRU, hybrid architectures) for pose recognition.  
- **Graph Construction:** Build a Directed Acyclic Graph (DAG) to represent poses and their transitions, with weighted edges.  
- **Feedback System:** Implement mechanisms to evaluate correctness based on execution speed and angular deviation.  
- **Evaluation:** Benchmark against baseline HAR frameworks to validate accuracy and robustness.  

---

## Future Plans  
- Extend recognition beyond Surya Namaskar to include **other yoga asanas** and more complex yoga sequences.  
- Incorporate **multi-sensor setups** (wrist, ankles, waist) to improve recognition accuracy.  
- Integrate the system into a **mobile or wearable application** for real-time feedback.  
- Investigate **transfer learning approaches** using publicly available HAR datasets to improve generalization.  
- Enhance the **feedback module** to provide detailed corrective guidance rather than only correctness scores.  

---

## Final Note:
Thank you for taking the time to explore my work.
I've done my best to make this project accurate, informative, and useful. I'm always learning, so if you have feedback or ideas, feel free to reach out! I'm open to suggestions, improvements, and feedback!


*Yoga4All combines **ubiquitous computing**, **wearable sensors**, and **deep learning** to make yoga practice smarter, accessible, and trainer-free.*
