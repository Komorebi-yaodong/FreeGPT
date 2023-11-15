![ref1]

**Evaluation Only. Created with Aspose.Words. Copyright 2003-2023 Aspose Pty Ltd.**

Intro to Observability Quantifying Observability Observability Properties Controllers & Observers Design Observer-Based Control

![](EE5143_Module8.002.png) ![](EE5143_Module8.003.png) ![](EE5143_Module8.004.png) ![](EE5143_Module8.005.png) ![](EE5143_Module8.006.png)

Module 08![](EE5143_Module8.007.png)

Observability and State Estimator Design of Dynamical LTI Systems

**Ahmad F. Taha**

**EE 5143: Linear Systems and Control** Email: ahmad.taha@utsa.edu

Webpage: <http://engineering.utsa.edu/ataha>

![](EE5143_Module8.008.png) ![](EE5143_Module8.009.png)

November 7, 2017

©**Ahmad F. Taha Module 08 — Observability and State Estimator Design of Dynamical LTI Systems** 1 / 24![ref2]
**Created with an evaluation copy of Aspose.Words. To discover the full versions of our APIs please visit: https://products.aspose.com/words/**
![ref3]

**Evaluation Only. Created with Aspose.Words. Copyright 2003-2023 Aspose Pty Ltd.**

Intro to Observability Quantifying Observability Observability Properties Controllers & Observers Design Observer-Based Control

Observability for CT Systems![](EE5143_Module8.012.png)

The previous derivation for observability was for DT LTI systems What if we have a CT LTI system? Do we obtain the same observability testing conditions?

Yes, we do!

First, note that the control input u(t) plays no role in observability, just like how the output y(t) plays no role in controllability

To see that, consider the following system with n states, p outputs, where (again) we want to obtain x(t0) (unknown):

**Created with an evaluation copy of Aspose.Words. To discover the full versions of our APIs please visit: https://products.aspose.com/words/**
![ref4]

x˙(t) = Ax(t)*,*

y(t0) = y˙(t0) = y¨(t0) =

...

y(n− 1)(t0) =

y(t) = Cx(t) x(t0) = x0 =⇒

Cx(t0)

Cx˙(t0) = CAx(t0)

Cx¨(t0) = CA2x(t0)

Cx(n− 1)(t0) = CAn− 1x(t0)

**Created with an evaluation copy of Aspose.Words. To discover the full versions of our APIs please visit: https://products.aspose.com/words/**
![ref3]

©**Ahmad F. Taha Module 08 — Observability and State Estimator Design of Dynamical LTI Systems** 10 / 24![ref2]
**Created with an evaluation copy of Aspose.Words. To discover the full versions of our APIs please visit: https://products.aspose.com/words/**
![ref3]

**Evaluation Only. Created with Aspose.Words. Copyright 2003-2023 Aspose Pty Ltd.**

Intro to Observability Quantifying Observability Observability Properties Controllers & Observers Design Observer-Based Control

Observability for CT LTI Systems — 2![](EE5143_Module8.014.png)

We can write the previous equation as:

 y(t )   

0 C

 − 1).  CAn− 1

y˙(t0)  CA 

 y¨(..t0) Y(t0) =  ... x(t0) ⇒ y(n (t0) ![](EE5143_Module8.015.png) ![](EE5143_Module8.016.png)

= O∈ Rnp× n

x(t0) = O￿Y(t0) = ( O  O)− 1OY(t0)

Hence, the initial conditions can be determined if the observability matrix is full column rank

This condition is identical to the DT case where we also wanted to obtain x(k = 0) from a set of output measurements

The difference here is that we had to obtain derivatives of the output at t0

Can you rederive the equations if u(t)  = 0? It won’t make an impact on whether a solution exists, but it’ll change x(t0)

©**Ahmad F. Taha Module 08 — Observability and State Estimator Design of Dynamical LTI Systems** 11 / 24![ref2]
**Created with an evaluation copy of Aspose.Words. To discover the full versions of our APIs please visit: https://products.aspose.com/words/**
![ref3]

**Evaluation Only. Created with Aspose.Words. Copyright 2003-2023 Aspose Pty Ltd.**

Intro to Observability Quantifying Observability Observability Properties Controllers & Observers Design Observer-Based Control

Controllability-Observability Duality, Minimality![](EE5143_Module8.017.png)

Duality![](EE5143_Module8.018.png)

The CT LTI system with state-space matrices (A˜ *,*B˜ *,*C˜ *,*D˜ ) is called the **dual** of another CT LTI system with state-space matrices (A*,*B*,*C*,*D) if

A˜ = A *,* B˜ = C *,* C˜ = B *,* D˜ = D *.* Controllability-Observability Duality![](EE5143_Module8.019.png)

CT system (A*,*B*,*C*,*D) is observable (controllable) if and only if its dual system (A˜ *,* B˜ *,* C˜ *,* D˜ ) is controllable (observable).

Minimality![](EE5143_Module8.020.png)

A system (A*,*B*,*C*,*D) is called minimal if and only if it is both controllable and observable.

©**Ahmad F. Taha Module 08 — Observability and State Estimator Design of Dynamical LTI Systems** 12 / 24![ref2]
**Created with an evaluation copy of Aspose.Words. To discover the full versions of our APIs please visit: https://products.aspose.com/words/**
![ref3]

**Evaluation Only. Created with Aspose.Words. Copyright 2003-2023 Aspose Pty Ltd.**

Intro to Observability Quantifying Observability Observability Properties Controllers & Observers Design Observer-Based Control

Observer Design![](EE5143_Module8.021.png)

![](EE5143_Module8.022.png)

Objective here is to estimate (in real-time) the state of the actual system x(t) given that ICs x(0) are not known

To do that, we design an observer—dynamic state estimator (DSE) Define dynamic estimation error: e(t) = x(t) − xˆ(t)

Error dynamics:

e˙(t) = x˙ (t) − xˆ˙(t) = (A− LC)(x(t) − xˆ(t)) = (A− LC)e(t)

Hence, e(t) → 0*,*as t → ∞ if eig(A− LC) *<* 0 **Objective:** design observer/estimator gain L such that

eig(A− LC) *<* 0 or at a certain location![ref2]

©**Ahmad F. Taha Module 08 — Observability and State Estimator Design of Dynamical LTI Systems** 13 / 24
**Created with an evaluation copy of Aspose.Words. To discover the full versions of our APIs please visit: https://products.aspose.com/words/**
![ref3]

**Evaluation Only. Created with Aspose.Words. Copyright 2003-2023 Aspose Pty Ltd.**

Intro to Observability Quantifying Observability Observability Properties Controllers & Observers Design Observer-Based Control

Example — Controller Design![](EE5143_Module8.023.png)

1 3 1

Given a system characterized by A = *,*B =

3 1 0

Is the system stable? What are the eigenvalues? **Solution:** unstable, eig(A) = 4*,*−2

Find linear state-feedback gain K (i.e., u = −Kx), such that the poles of the closed-loop controlled system are −3 and −5

Characteristic polynomial: *λ* 2 + ( k1 − 2)*λ* + (3 k2 − k1 − 8) = 0 **Solution:** u = −Kx = −[10 11] x1 = −10x1 − 11x2

x2

MATLAB command: K = place(A,B,eig~~ desired)

1 0 1

What if A = *,*B = , can we stabilize the system?

0 1 1

©**Ahmad F. Taha Module 08 — Observability and State Estimator Design of Dynamical LTI Systems** 14 / 24![ref2]
**Created with an evaluation copy of Aspose.Words. To discover the full versions of our APIs please visit: https://products.aspose.com/words/**
![ref3]

**Evaluation Only. Created with Aspose.Words. Copyright 2003-2023 Aspose Pty Ltd.**

Intro to Observability Quantifying Observability Observability Properties Controllers & Observers Design Observer-Based Control

Example — Observer Design![](EE5143_Module8.024.png)

**Created with an evaluation copy of Aspose.Words. To discover the full versions of our APIs please visit: https://products.aspose.com/words/**
![ref5]

1 Given a system characterized by A =

3

Find linear state-observer gain L= [l1 l2]  estimation error are −5 and −3

3

*,*C = 0*.*5 1

1

such that the poles of the

**Created with an evaluation copy of Aspose.Words. To discover the full versions of our APIs please visit: https://products.aspose.com/words/**
![ref3]

Characteristic polynomial:

*λ* 2 + ( −2 + l2 + 0 *.*5l1)*λ* + ( −8 + 0 *.*5l2 + 2 *.*5l1) = 0

8

**Solution:** L=

6

MATLAB command: L= place(A’,C’,eig~~ desired)

©**Ahmad F. Taha Module 08 — Observability and State Estimator Design of Dynamical LTI Systems** 15 / 24![ref2]
**Created with an evaluation copy of Aspose.Words. To discover the full versions of our APIs please visit: https://products.aspose.com/words/**
![ref3]

**Evaluation Only. Created with Aspose.Words. Copyright 2003-2023 Aspose Pty Ltd.**

Intro to Observability Quantifying Observability Observability Properties Controllers & Observers Design Observer-Based Control

Observer, Controller Design for DT Systems—Summary![](EE5143_Module8.026.png)

For CT system

x˙(t) = Ax(t) + Bu(t)*,* y(t) = Cx(t) + Du(t)

- To design a stabilizing controller, find K such that eig(Acl) = eig(A− BK) *<* 0

  or at a prescribed location

- To design a converging estimator (observer), find L such that

eig(Acl) = eig(A− LC) *<* 0

or at a prescribed location What if the system is DT?

x(k + 1) = Ax(k) + Bu(k)*,* y(k) = Cx(k) + Du(k)

- To design a stabilizing controller, find K such that

−1 *<* eig(Acl) = eig(A− BK) *<* 1 or at a prescribed location

- To design a converging estimator (observer), find L such that

−1 *<* eig(Acl) = eig(A− LC) *<* 1 or at a prescribed location![ref2]

©**Ahmad F. Taha Module 08 — Observability and State Estimator Design of Dynamical LTI Systems** 16 / 24
**Created with an evaluation copy of Aspose.Words. To discover the full versions of our APIs please visit: https://products.aspose.com/words/**
![ref3]

**Evaluation Only. Created with Aspose.Words. Copyright 2003-2023 Aspose Pty Ltd.**

Intro to Observability Quantifying Observability Observability Properties Controllers & Observers Design Observer-Based Control

Observer Design![](EE5143_Module8.027.png)

What if the system dynamics are:

x˙(t) = Ax(t) + Bu(t)*,* y(t) = Cx(t) + Du(t) The observer dynamics will then be:

xˆ˙(t) = Axˆ(t) + Bu(t) + L(y(t) − yˆ(t))

Hence, the control input shouldn’t impact the estimation error Why? Because the input u(t) is know!

Estimation error:

e(t) = x(t) − xˆ(t) =⇒ e˙(t) = x˙ (t) = xˆ˙(t) = (A− LC)(x(t) − xˆ(t))

=⇒ e˙(t) = (A− LC)e(t)

©**Ahmad F. Taha Module 08 — Observability and State Estimator Design of Dynamical LTI Systems** 17 / 24![ref2]
**Created with an evaluation copy of Aspose.Words. To discover the full versions of our APIs please visit: https://products.aspose.com/words/**
![ref3]

**Evaluation Only. Created with Aspose.Words. Copyright 2003-2023 Aspose Pty Ltd.**

Intro to Observability Quantifying Observability Observability Properties Controllers & Observers Design Observer-Based Control

MATLAB Example![](EE5143_Module8.028.png)

15~~ A=[1 -0.8; 1 0];![](EE5143_Module8.029.png)

x1 B=[0.5; 0];

10 xˆ C=[1 -1];

1 % Selecting desired poles

5 eig\_desired=[.5 .7];

0 L=place(A’,C’,eig\_desired)’;

- Initial state

-5 x=[-10;10];

- Initial estimate

-10 xhat=[0;0];

- Dynamic Simulation

-15 XX=x;

-20~~ XXhat=xhat;

0 1 2 3 4 5 6 7 8 9 10 T=10;

Time (seeconds) % Constant Input Signal

UU=.1\*ones(1,T);

for k=0:T-1,

15~~ u=UU(k+1);![](EE5143_Module8.030.png)

x2 y=C\*x;

10 yhat=C\*xhat;

xˆ

5 2 x=A\*x+B\*u;

xhat=A\*xhat+B\*u+L\*(y-yhat); 0 XX=[XX,x];

-5 XXhat=[XXhat,xhat];

end

-10 % Plotting Results

-15 subplot(2,1,1)

plot(0:T,[XX(1,:);XXhat(1,:)]); -20 subplot(2,1,2)

plot(0:T,[XX(2,:);XXhat(2,:)]); -25

0 1 2 3 4 5 6 7 8 9 10

Time (seeconds)

©**Ahmad F. Taha Module 08 — Observability and State Estimator Design of Dynamical LTI Systems** 18 / 24![ref2]
**Created with an evaluation copy of Aspose.Words. To discover the full versions of our APIs please visit: https://products.aspose.com/words/**
![ref3]

**Evaluation Only. Created with Aspose.Words. Copyright 2003-2023 Aspose Pty Ltd.**

Intro to Observability Quantifying Observability Observability Properties Controllers & Observers Design Observer-Based Control

Observer-Based Control — 1![](EE5143_Module8.031.png)

Recall that for LSF control: u(t) = −Kx(t)

What if x(t) is not available, i.e., it can only be estimated? **Solution:** get xˆ by designing L

Apply LSF control using xˆ with a LSF matrix K to both the original system and estimator

**Question:** how to design K and L simultaneously? Poles of the closed-loop system?

This is called an observer-based controller (OBC)

**This document was truncated here because it was created in the Evaluation Mode.**
**Created with an evaluation copy of Aspose.Words. To discover the full versions of our APIs please visit: https://products.aspose.com/words/**

[ref1]: EE5143_Module8.001.png
[ref2]: EE5143_Module8.010.png
[ref3]: EE5143_Module8.011.png
[ref4]: EE5143_Module8.013.png
[ref5]: EE5143_Module8.025.png
