---
TITLE: Yoga4All
AUTHOR: Priyanka Rajeev Hichkad
---

Yoga4All is a **Ubiquitous Computing project** under the guidance of **Prof. Hari Prabhat Gupta, Department of Computer Science and Engineering, IIT BHU**.  
The project leverages **wearable motion sensors** to recognize yoga poses, focusing initially on *Surya Namaskar (Sun Salutation)*, and aims to provide feedback on correctness and performance analysis.  

---

## Project Overview  
Yoga4All is designed to make yoga practice smarter and more accessible by utilizing **time-series sensor data** rather than vision-based methods. Sensor readings are collected using **MPU-9250 IMU** and **custom-built motion sensors** developed by our senior, which provide **accelerometer, gyroscope, magnetometer and timestamp data** stored in CSV format.  

The project objectives are:  
- Detect and classify yoga poses using **deep learning sequence models** (ANN, RNN, LSTM, GRU, and related architectures).  
- Construct a **Directed Acyclic Graph (DAG)** where nodes represent poses and edges represent transition times.  
- Develop **feedback mechanisms** for evaluating execution speed, angular deviation, and overall correctness.  
- Expand the system beyond Surya Namaskar to accommodate broader yoga practices in future work.  

---

## Current Progress  

**Week 1:**  
- Conducted the initial meeting to understand the **project objectives**, overall workflow, and division of responsibilities among team members.  
- Reviewed the research paper *YogaHelp: Leveraging Motion Sensors for Learning Correct Execution of Yoga with Feedback* to gain clarity on the methodology, data flow, and correctness evaluation framework.  

**Week 2:**  
- Explored the **three types of motion sensors** being used in the project; two were procured, while two were designed by our senior.  
- Understood that the sensors record data in **CSV format** containing accelerometer, gyroscope, magnetometer and timestamp readings.  
- Learned about the project’s **REST API (Swagger)**, which enables data upload and remote access for experimentation and analysis.  

**Week 3:**  
- Initiated **data collection** by performing Surya Namaskar with wrist-mounted sensors, with parallel video recordings for validation.  
- The dataset was collected from **seven participants**, each performing **ten sets weekly** (one set consisting of two complete Surya Namaskars).
- Conducted additional data collection at the **Student Activity Centre (SAC)** to capture Surya Namaskar performed with proper form.

**Week 4:**  
- Continued performing **Surya Namaskar** while wearing **two sensors** developed by our seniors, each capturing around **7–8 readings per second**. One sensor was worn on the **right wrist** and the other on the **left ankle** to capture upper and lower body movement simultaneously.  
- Data collection was **simultaneously validated through video recordings from three different angles**—front, side, and back—to ensure accurate mapping of poses and transitions.  

**Week 5:**  
- The collected dataset was **manually labeled** by adding a *Position* column, marking poses from **1 to 12**, validated through synchronized **video and sensor timestamps**.  
- Integrated **wrist and ankle sensor data** based on timestamp alignment to create a unified dataset for model training.  
- Performed **data preprocessing** to remove unwanted rows such as transition data and break time segments, ensuring cleaner inputs for modeling.  

**Week 6:**  
- Studied a **Human Activity Recognition (HAR) model** from Kaggle to identify strategies applicable to our dataset.
- Explored **deep learning architectures (ANN, CNN, RNN, LSTM)** to identify suitable models for pose recognition and sequence learning.

**Week 7:**  
- Developed a **GridSearchCV-based optimization pipeline** combined with a **Keras LSTM model** (wrapped using **SciKeras**) to systematically experiment with model architectures, hyperparameters, and input sequence lengths.  
- This approach automates and optimizes the selection of **network layers, units, dropout, activation functions, optimizers, loss functions, batch size, and epochs**, enabling the identification of the best-performing configuration for **human activity recognition using time-series sensor data**.  

**Week 8:**  
- Evaluated the trained **LSTM-based model** using **an external participant’s dataset** to test generalization and real-world performance, followed by necessary updates and fine-tuning.  
- Implemented a program to generate a **Directed Acyclic Graph (DAG)** representing the **12 Surya Namaskar poses** as nodes and their **sequential transitions** as directed edges.  
- Each edge was weighted by the **average time difference (Δt)** between consecutive poses derived from the sensor data. The DAG visualization was designed in a clean linear layout with clearly labeled nodes and edge weights displayed.

---

## Next Steps  
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
