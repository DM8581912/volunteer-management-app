import React from "react";
import { Formik, Form, Field, ErrorMessage } from "formik";
import * as Yup from "yup";
import styles from "./Event.module.css";
import DatePicker from 'react-datepicker';

// import 'react-datepicker/dist/react-datepicker.css';


// Validation schema using Yup
const EventSchema = Yup.object().shape({
  eventName: Yup.string().min(100, "Event name must be at least 100 characters").required("Required"),
  eventDescription: Yup.string().required("You must enter a description"),
  location: Yup.string().required("You must enter a location"),
  requiredSkills: Yup.array().min(1, 'At least one skill is required').required('Required'), 
  urgency: Yup.string().required('Urgency is required'), // Required dropdown
  eventDate: Yup.date().required('Event date is required'), // Date picker validation



  // email: Yup.string().email("Invalid email address").required("Required"),
  // password: Yup.string().min(6, "Password must be at least 6 characters").required("Required"),
  // confirmPassword: Yup.string()
  //   .oneOf([Yup.ref("password"), null], "Passwords must match")
  //   .required("Required"),
});

const Event = () => {
   return (
    <div className={styles.eventContainer}>
      <h2>Event Management Form</h2>
      <Formik
        initialValues={{
          eventName: "",
          eventDescription: "",
          location: "",
          requiredSkills: [],
          urgency: '',
          eventDate: null,
        }}
        validationSchema={EventSchema}
        onSubmit={(values) => {
          console.log("Registration successful!", values);
          alert("Registration successful!");
        }}
      >
        {({values,setFieldValue,isSubmitting }) => (
          <Form>
           <div>
            <label htmlFor="eventName">Event Name</label>
            <Field type="text" name="eventName" />
            <ErrorMessage name="eventName" component="div" className={styles.error} />
           </div>
           <div>
            <label htmlFor="eventDescription">Event Description</label>
            <Field as="textarea" name="eventDescription"/>
            <ErrorMessage name="eventDescription" component="div" className={styles.error} />
           </div>
           <div>
            <label htmlFor="location">Location</label>
            <Field as="textarea" name="location"/>
            <ErrorMessage name="location" component="div" className={styles.error} />
           </div>
           
           <div>
             <label htmlFor="requiredSkills">Required Skills</label>
             <Field
               as="select"
               name="requiredSkills"
               multiple={true}
               onChange={(event) => {
                 const selectedOptions = Array.from(event.target.selectedOptions, (option) => option.value);
                 setFieldValue('requiredSkills', selectedOptions); // Manually set selected values
               }}
             >
               <option value="JavaScript">JavaScript</option>
               <option value="Python">Python</option>
               <option value="React">React</option>
               <option value="Node.js">Node.js</option>
             </Field>
             <ErrorMessage name="requiredSkills" component="div" className={styles.error} />
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

           <button type="submit" disabled={isSubmitting}>
             Submit
           </button> 
          </Form>
        )}
      </Formik>
    </div>
  );
}

export default Event;