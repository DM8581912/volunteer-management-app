import React from "react";
import { Formik, Form, Field, ErrorMessage } from "formik";
import * as Yup from "yup";
import styles from "./Event.module.css";
import {useState} from 'react';
import Select from 'react-select';
import DatePicker from "react-datepicker";
import "react-datepicker/dist/react-datepicker.css";

// Validation schema using Yup
// const EventSchema = Yup.object().shape({
//   eventName: Yup.string().min(100, "Event name must be at least 100 characters").required("Required"),
//   eventDescription: Yup.string().required("You must enter a description"),
//   location: Yup.string().required("You must enter a location"),
//   requiredSkills: Yup.string().required('One Skill is required'),
//   urgency: Yup.string().required('Urgency is required'),
//   eventDate: Yup.date().required('Event date is required'),
// });

// const options = [
//   { value: 'Carry over 50 lbs', label: 'Carry over 50 lbs' },
//   { value: 'Run over 20 miles', label: 'Run over 50 miles' },
// ];

// const customStyles = {
//   control: (base, state) => ({
//     ...base,
//     height: 40,
//     fontSize: 14,
//     overflow: 'visible',

//   }),
//    multiValue: (base) => ({
//      ...base,
//      height: 30,
//      overflow: 'visible',

//   }),
//   multiValueLabel: (base) => ({
//    ...base,
//    overflow: 'visible',
//   }),
//   indicatorSeparator: () => ({ display: "none" }),
// };

// const Event = () => {
//   const [startDate, setStartDate] = useState(new Date());

//   const [selectedOption, setSelectedOption] = useState(null);
//   const [isValid, setIsValid] = useState(true);


//   const handleSubmit = (e) => {
//     e.preventDefault();
//     if (!selectedOption) {
//       setIsValid(false); // Set validation error if no option is selected
//     } else {
//       setIsValid(true);
//       // Process the form
//       console.log('Selected:', selectedOption);
//     }
//   };

//   return (
//     <div className={styles.eventContainer}>
//       <h2>Event Management Form</h2>
//       <Formik
//         initialValues={{
//           eventName: "",
//           eventDescription: "",
//           location: "",
//           requiredSkills: [],
//           urgency: '',
//           eventDate: null,
//         }}
//         validationSchema={EventSchema}
//         onSubmit={(values) => {
//           console.log("Registration successful!", values);
//           alert("Registration successful!");
//         }}
//       >
//         {({setFieldValue, isSubmitting }) => (
//           <Form onSubmit={handleSubmit}>
//             <div>
//               <label htmlFor="eventName">Event Name</label>
//               <Field type="text" name="eventName" />
//               <ErrorMessage name="eventName" component="div" className={styles.error} />
//             </div>
//             <div>
//               <label htmlFor="eventDescription">Event Description</label>
//               <Field as="textarea" name="eventDescription" />
//               <ErrorMessage name="eventDescription" component="div" className={styles.error} />
//             </div>
//             <div>
//               <label htmlFor="location">Location</label>
//               <Field as="textarea" name="location" />
//               <ErrorMessage name="location" component="div" className={styles.error} />
//             </div>

//             {/* Multi-select for Required Skills */}
//             <div>
//              <div>Required Skills</div>
//              <Select
//                 onChange={setSelectedOption}
//                 options={options}
//                 placeholder="Select an option"
//                 isMulti
//                 styles={customStyles}
//               />
//               {!isValid && <p style={{ color: 'red' }}>This field is required</p>}
//             </div>
  
//             {/* Dropdown for Urgency */}
//             <div>
//               <label htmlFor="urgency">Urgency</label>
//               <Field as="select" name="urgency">
//                 <option value="">Select urgency</option>
//                 <option value="low">Low</option>
//                 <option value="medium">Medium</option>
//                 <option value="high">High</option>
//               </Field>
//               <ErrorMessage name="urgency" component="div" className={styles.error} />
//             </div>

//             <div>
//              <div>Select Date</div>
//              <DatePicker selected={startDate} onChange={(date) => setStartDate(date)} />
//             </div>



//             <button type="submit">Submit</button>
//           </Form>
//         )}
//       </Formik>
      
  

 
//     </div>
//   );
// };


// Validation schema using Yup
const EventSchema = Yup.object().shape({
  eventName: Yup.string().min(10, "Event name must be at least 10 characters").required("Required"),
  eventDescription: Yup.string().required("You must enter a description"),
  location: Yup.string().required("You must enter a location"),
  urgency: Yup.string().required("Urgency is required"),
  eventDate: Yup.date().required("Event date is required"),
});

const options = [
  { value: "Carry over 50 lbs", label: "Carry over 50 lbs" },
  { value: "Run over 20 miles", label: "Run over 20 miles" },
];

const customStyles = {
  control: (base) => ({
    ...base,
    height: 40,
    fontSize: 14,
  }),
};

const Event = () => {
  const [startDate, setStartDate] = useState(new Date());
  const [selectedOption, setSelectedOption] = useState([]);
  const [isValid, setIsValid] = useState(true);

  const handleSubmit = async (values) => {
    if (!selectedOption.length) {
      setIsValid(false);
      return;
    }

    const eventData = {
      ...values,
      requiredSkills: selectedOption.map((option) => option.value), // Integrate react-select values
      eventDate: startDate, // Integrate DatePicker value
    };

    console.log("Final event data:", eventData);

    // Send POST request to the backend
    try {
      const response = await fetch("http://localhost:5000/eventform", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(eventData),
      });

      if (response.ok) {
        const result = await response.json();
        alert("Event created successfully: " + JSON.stringify(result));
      } else {
        const error = await response.json();
        alert("Error creating event: " + JSON.stringify(error));
      }
    } catch (error) {
      console.error("Error:", error);
    }
  };

  return (
    <div className={styles.eventContainer}>
      <h2>Event Management Form</h2>
      <Formik
        initialValues={{
          eventName: "",
          eventDescription: "",
          location: "",
          urgency: "",
        }}
        validationSchema={EventSchema}
        onSubmit={handleSubmit}
      >
        {({ setFieldValue }) => (
          <Form>
            <div>
              <label htmlFor="eventName">Event Name</label>
              <Field type="text" name="eventName" />
              <ErrorMessage name="eventName" component="div" className={styles.error} />
            </div>
            <div>
              <label htmlFor="eventDescription">Event Description</label>
              <Field as="textarea" name="eventDescription" />
              <ErrorMessage name="eventDescription" component="div" className={styles.error} />
            </div>
            <div>
              <label htmlFor="location">Location</label>
              <Field as="textarea" name="location" />
              <ErrorMessage name="location" component="div" className={styles.error} />
            </div>

            {/* Multi-select for Required Skills */}
            <div>
              <div>Required Skills</div>
              <Select
                onChange={(option) => {
                  setSelectedOption(option);
                  setIsValid(true);
                }}
                options={options}
                placeholder="Select skills"
                isMulti
                styles={customStyles}
              />
              {!isValid && <p style={{ color: "red" }}>At least one skill is required</p>}
            </div>

            {/* Dropdown for Urgency */}
            <div>
              <label htmlFor="urgency">Urgency</label>
              <Field as="select" name="urgency">
                <option value="">Select urgency</option>
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
              </Field>
              <ErrorMessage name="urgency" component="div" className={styles.error} />
            </div>

            {/* Date picker for event date */}
            <div>
              <div>Select Date</div>
              <DatePicker
                selected={startDate}
                onChange={(date) => {
                  setStartDate(date);
                  setFieldValue("eventDate", date); // Update Formik state for eventDate
                }}
              />
              <ErrorMessage name="eventDate" component="div" className={styles.error} />
            </div>

            <button type="submit">Submit</button>
          </Form>
        )}
      </Formik>
    </div>
  );
};

export default Event;