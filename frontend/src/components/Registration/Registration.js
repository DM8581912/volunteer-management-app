import React from "react";
import { Formik, Form, Field, ErrorMessage } from "formik";
import * as Yup from "yup";
import styles from "./Registration.module.css";  // Import CSS module

// Validation schema using Yup
const RegistrationSchema = Yup.object().shape({
  email: Yup.string().email("Invalid email address").required("Required"),
  password: Yup.string()
    .min(6, "Password must be at least 6 characters")
    .required("Required"),
  confirmPassword: Yup.string()
    .oneOf([Yup.ref("password"), null], "Passwords must match")
    .required("Required"),
});

const Registration = () => {
  const dummyRegistrationData = {
    email: "dummyuser@example.com",
    password: "dummyPassword123",
    confirmPassword: "dummyPassword123",
  };

  return (
    <div className={styles.registrationContainer}>
      <h2 className={styles.heading}>Register</h2> 
      <Formik
        initialValues={dummyRegistrationData}
        validationSchema={RegistrationSchema}
        onSubmit={(values) => {
          console.log("Registration successful!", values);
          alert("Registration successful!");
        }}
      >
        {({ isSubmitting }) => (
          <Form>
            <div className={styles.formGroup}> 
              <label htmlFor="email">Email</label>
              <Field type="email" name="email" className={styles.input} /> 
              <ErrorMessage name="email" component="div" className={styles.error} /> 
            </div>

            <div className={styles.formGroup}> 
              <label htmlFor="password">Password</label>
              <Field type="password" name="password" className={styles.input} /> 
              <ErrorMessage name="password" component="div" className={styles.error} /> 
            </div>

            <div className={styles.formGroup}> 
              <label htmlFor="confirmPassword">Confirm Password</label>
              <Field type="password" name="confirmPassword" className={styles.input} /> 
              <ErrorMessage name="confirmPassword" component="div" className={styles.error} /> 
            </div>

            <button type="submit" disabled={isSubmitting} className={styles.button}>Register</button> 
          </Form>
        )}
      </Formik>
    </div>
  );
};

export default Registration;
