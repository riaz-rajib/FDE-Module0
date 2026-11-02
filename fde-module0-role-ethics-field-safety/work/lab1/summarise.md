
# Lab 1: Role-Boundary Case Review


***********************************************************************************************************************************

## Scenario Decision Sheet: FDE0-S01 (CivicFlow Services)


### 1. Scenario Baseline Summary
**Stated Outcome:** Reduce avoidable hand-offs without weakening decision authority or public-record controls (Time boundary is under a 10-working-day steering committee deadline).

**Affected People:** 
Sponsor: Controls discovery budget but faces friction regarding timeline expectations.
Service operations: Operations wants a manual fallback
Product Manager: Demands automation first.
Security adviser: Security control decision. A security representative is available twice each week.

**Authorized Environment:** 
Bounded prototype / learning environment using synthetic data only (generated case records).

**Hard Boundary**
No access to council production systems or identities.



### 2. Request Classification Matrix

**Request 1: Build a bounded case-routing workflow prototype using synthetic case records for the steering committee demonstration.**
  **Classification:** **Own**
  **Supporting Evidence:** 
   Technical evidence and bounded prototype. 
   Only generated case records may be used in the learning environment.

**Request 2: Define and sign off on the security control policies governing the new case-routing workflow.**
  **Classification:** **Contribute**
  **Supporting Evidence:** 
  The FDE provides technical evidence, but the participant profiles explicitly restrict "Security control decision" authority to the Security Adviser. The FDE must provide input to this adviser during their bi-weekly availability.

**Request 3: Review and certify the automated workflow against local public-record retention laws.**
  **Classification:** **Route**
  **Supporting Evidence:** 
  The known boundaries section strictly states that "Legal and records-retention conclusions require authorised specialists." The FDE does not hold legal authority and must direct this request to the designated compliance team.

**Request 4: Connect the demonstration prototype to the live council production system to display real-time user identities.**
  **Classification:** **Stop**
  **Supporting Evidence:** 
  The known boundaries state there is absolutely "No access to council production systems or identities." Furthermore, the facts explicitly show the Executive Sponsor "cannot approve production data access," making any attempt to connect to production a direct violation of operational boundaries.


### 3. Plausible Charter Change Analysis 


*** The Scenario Reality (Current Charter)***

Current Restriction:
The FDE is hit with a hard "Stop" if asked to connect the prototype to council production systems or use 
real user identities.

Reason: 
The Executive Sponsor lacks the organizational power to grant live data clearance ("cannot approve production data access"), and the known boundaries explicitly firewall council systems.



*** The Plausible Charter Change ***

• How the Answer Changes: 
  The "Stop" classification shifts to a "Contribute" or "Own" classification.

• The New Operational Reality: 
  The charter is officially modified to include a "Staging Environment Exception Clause." Under this revised charter, the FDE is granted authorized access to a strictly sandboxed staging environment that mirrors council.

***  Authorizing Authority ***

Security Adviser: 
Reveiw and accept the sandbox environment.

Higher Authrity:
Can grant permission to replicate data for sandbox.


--------------------------------------------------------------------------------------------------------------------------------------


**************************************************************************************************************************************

## Scenario Decision Sheet: FDE0-S02 (Harbour Referral Lab)

### 1. Scenario Baseline Summary
**Stated Outcome:** Reduce avoidable hand-offs without weakening decision authority or public-record controls.

**Affected People:** 
  Clinical sponsor
  Clinical safety officer
  Privacy adviser
  FDE
  Facilitator

**Authorized Environment:** 
A synthetic-only environment mapping and prototyping workflows using strictly generated records.

**Hard Boundary**
  Do not open or import any undeclared data file.
  Do not make clinical, privacy or legal determinations.



### 2. Request Classification Matrix

 **Request 1: Map and prototype the referral-status tracking dashboard using completely generated medical records.**

   **Classification:** **Own**
   **Supporting Evidence: The participant table explicitly assigns the FDE authority over the `"Synthetic technical experiment"`. The customer request explicitly authorizes mapping and prototyping a referral-status workflow using `"generated records."`

**Request 2: Evaluate a facilitator-provided spreadsheet to verify if it is safely de-identified for future project integration.**
  **Classification:** **Stop**
  **Supporting Evidence:** Known boundaries strictly command: `"Do not open or import any undeclared data file"` and `"Do not make   clinical, privacy or legal determinations."` The facilitator has presented a spreadsheet without supporting evidence; interacting with it violates both constraints.

**Request 3: Approve and sign off on the data retention period policies for future records storage as requested by the sponsor.**

  **Classification:** **Stop**
  **Supporting Evidence:** The visible tensions note that the sponsor wants the FDE to approve the retention window. However, known boundaries state explicitly: `"Do not make clinical, privacy or legal determinations."` Data retention is a legal and privacy governance issue, meaning the FDE must halt this request immediately.

**Request 4: Determine if a proposed future secondary use of the referral data matches local healthcare privacy regulations.**

  **Classification:** **Route**
  **Supporting Evidence:** The facts state that `"The privacy adviser must decide whether a proposed future data use is permitted."` The participant profile grants them absolute `"Privacy interpretation"` authority. The FDE must route this request directly to them.


### 3. Strategic Charter Nuance

**Plausible Change in Classification:** 

  The **"Stop"** classification on assessing data retention rules could change to **"Contribute."** This would occur if the operational charter shifted from an isolated technical spike to an integrated project steering phase where the FDE is tasked with providing technical performance data on how different retention periods affect database storage scale.
 

**Authorizing Authority:** This change cannot be authorized by the Clinical Sponsor. It requires explicit, written sign-off from the **Privacy Adviser** (who governs privacy compliance) and the **Clinical Safety Officer** (to ensure data lifecycle changes do not impact patient safety).




