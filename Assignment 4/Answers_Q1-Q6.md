# Assignment 4 — Mobile Computing Architecture, Runtime, Security and Power Design

**Scope and method.** This is a design-only submission. The assignment explicitly prohibits IDEs, emulators, SDKs and source code. Therefore, the implementation evidence is expressed as layered specifications, decision tables, state-transition patterns, test vectors, traces and expected results. No executable program is included.

**Platform selection for platform-specific designs:** Android (Linux kernel, Android framework, ART runtime, Binder IPC). The historical Dalvik model is discussed where the question explicitly asks for Dalvik. Modern Android devices use ART, not Dalvik.

---

# Task 1 — Architecture Review (6 Marks)

## 1.1 Diagnose the draft (2 marks)

| No. | Technical deficiency | Why an engineer cannot build or evaluate it reliably |
|---|---|---|
| 1 | The design omits device drivers and the Hardware Abstraction Layer (HAL). | There is no defined path from framework requests to a camera, radio, sensor, display or storage controller. Hardware-specific responsibilities and interfaces are unknown. |
| 2 | It omits native system libraries and framework system services. | Applications need defined APIs for graphics, media, databases, networking, location and notifications. A framework cannot be implemented from the vague statement that developers use it. |
| 3 | “A kernel sits in the middle and runs the applications” assigns the wrong responsibility. Android uses a Linux monolithic kernel with loadable modules. The kernel schedules processes and threads, manages virtual memory, drivers, networking and low-level security; Android application lifecycle and framework callbacks are managed in user space. | Process creation, scheduling, system-call boundaries and responsibility for application lifecycle cannot be inferred. The kernel does not directly execute application business logic. |
| 4 | “Runtime” is undefined. It does not distinguish DEX bytecode from native machine code or explain interpretation, JIT and AOT compilation. | Engineers cannot determine the delivered artifact, compilation point, startup cost, ABI dependency or runtime services. |
| 5 | “Permissions” does not identify the authority, grant time or enforcement point. | Android permissions are declared by an app, evaluated/granted by the package and permission managers (with user consent for runtime/dangerous permissions), and enforced through framework checks, Binder identity checks and/or kernel mechanisms such as UID isolation and SELinux. The draft gives no enforceable access-control design. |
| 6 | “Saves battery when needed” has no trigger or mechanism. | There is no specified battery threshold, idle condition, suspend policy, wake-lock limit, job scheduling policy or push wake-up path. Power behaviour cannot be tested. |
| 7 | The app-to-OS boundary and IPC path are missing. | It is unclear whether an app calls a library, framework service, Binder interface or system call. Data validation, identity propagation and error handling cannot be designed. |
| 8 | No process isolation, application sandbox, or lifecycle boundary is stated. | Engineers cannot determine which app owns a process, how data is isolated, or what happens when the process is killed. |

## 1.2 Repaired layered specification — Android (3 marks)

Layers are listed from hardware upward. Each row states the contract exposed upward and dependency below.

| Layer | Responsibility | Exposes to layer above | Depends on layer below |
|---|---|---|---|
| 0. Physical hardware | CPU, RAM, flash storage, display, sensors, Wi-Fi/cellular modem, battery and power controller. | Interrupts, registers, DMA, radio/network events and physical resources through device controllers. | Electrical power, board wiring and firmware. |
| 1. Linux device drivers and kernel | Android uses the Linux monolithic kernel (with loadable modules). Drivers control devices. Kernel manages process/thread scheduling, virtual memory, filesystems, networking, sockets, interrupts, synchronization and low-level access control. | System-call interface, device nodes, sockets, Binder driver, memory and scheduling primitives. | CPU/MMU, hardware interrupts, device registers and firmware. |
| 2. Hardware Abstraction Layer (HAL) | Standardises hardware-specific services such as audio, camera, sensors, Bluetooth and radio. Vendor implementations translate common interfaces to device-specific drivers. | Stable hardware service interfaces to native daemons and framework services. | Kernel drivers, device firmware and vendor libraries. |
| 3. Native libraries and Android runtime support | C/C++ libraries provide graphics, media codecs, SQLite, SSL/TLS, libc and other low-level capabilities. ART executes DEX-based app code; JNI provides controlled calls between managed code and native libraries. | Native APIs, JNI, runtime services and library interfaces. | Kernel system calls, HAL interfaces and mapped native libraries. |
| 4. Android system services and application framework | Activity Manager, Package Manager, Permission Manager, Window Manager, Notification Manager, Connectivity, Location and Power Manager coordinate system functions. Framework APIs define app lifecycle and services. | Java/Kotlin framework APIs, lifecycle callbacks, content providers, notifications, jobs and Binder service contracts. | Native libraries, ART, HAL-backed services and Binder/kernel IPC. |
| 5. Application runtime and app process | Zygote creates app processes; ART loads DEX/OAT artifacts, verifies/executes code, performs JIT/AOT compilation as appropriate, garbage collection and thread management. App components run in a UID sandbox. | App classes, managed objects, callbacks, JNI and framework API calls. | Framework services, ART runtime, native libraries and Linux process/memory services. |
| 6. Application components and UI | Activities, services, receivers and providers implement product behaviour and UI. | User-visible screens, app-specific APIs and requests to framework services. | App runtime, framework APIs and granted permissions. |

**Explicit component placement and paths**

- **Kernel:** Layer 1, Linux monolithic kernel. It schedules and isolates processes; it does not own application lifecycle logic.
- **Runtime:** Layer 5, ART in current Android. Dalvik is the historical predecessor. ART executes DEX-derived code and manages memory/threads.
- **Security enforcement:** Application identity is assigned by Package Manager; runtime permissions are decided by Permission Manager and user consent; framework services check permissions; Binder carries caller identity; Linux UID/process isolation and SELinux enforce lower-level boundaries. Enforcement is therefore distributed, not a single “permissions layer.”
- **Power management:** Power Manager and DeviceIdle/Doze policy reside in system services (Layer 4), cooperating with kernel suspend/wakeup and wakelock mechanisms (Layer 1). Apps request bounded work through jobs/alarms or acquire justified, time-limited wake locks; they do not keep the CPU awake permanently.
- **Application-to-OS request path:** App component → framework API → Binder IPC to a system service → native service/HAL if required → kernel driver → hardware. Return values and callbacks travel back through the service/framework to the app process.

## 1.3 Design defence (≤100 words) (1 mark)

This is an architectural specification because it names concrete layers, assigns bounded responsibilities, defines interfaces between adjacent layers and identifies dependencies. It locates the Linux kernel, HAL, native libraries, ART, framework services, permission checks and power controls. It also defines the application-to-service path through framework APIs and Binder, then down through drivers to hardware. These details allow engineers to allocate components, identify trust boundaries and design tests. A marketing overview would describe benefits; this specification states mechanisms, ownership and observable interfaces.

---

# Task 2 — Platform Requirement and Architectural Comparison (8 Marks)

## 2.1 Model the requirement (2 marks)

| Element | Definition for the messaging product |
|---|---|
| Input | Platform architecture facts for Android, iOS and Windows: kernel family, driver/system-call boundary, app runtime, background execution policy, push service, sandbox, IPC and power policy. |
| Output | A platform comparison and a set of implementation decisions for message receipt, notification, secure storage, retry and user-visible delivery. |
| Objective | Deliver messages securely and promptly while the app is backgrounded, with bounded battery use on all three platforms. |
| Constraints | OS may suspend or terminate app processes; radio may be intermittent; messages must not be exposed to other apps; background execution is quota/policy controlled; user notification must be timely without a permanent CPU wake lock. |
| Decision | Use each platform's native push and background APIs behind a common server protocol, rather than assuming one continuously running cross-platform background process. |
| Information needed | Kernel/process model, runtime/code model, app lifecycle, push transport, notification service, permission model, sandbox, IPC, background quotas, force-stop/force-quit behaviour and power manager. |

## 2.2 Hypothesis (1 mark)

The largest effect on background delivery will come from each OS's **background process and push-notification policy**, rather than the kernel family alone, because a suspended or terminated app cannot receive a socket callback until the OS-approved push service wakes or launches an eligible app handler.

## 2.3 Comparison matrix (3 marks)

| Dimension | Android | iOS | Windows |
|---|---|---|---|
| Kernel family and structure | Linux kernel: monolithic kernel with loadable modules; Android adds Binder and SELinux integration. | Darwin/XNU: hybrid kernel combining Mach facilities with BSD subsystems and I/O Kit driver architecture. | Windows NT: hybrid kernel design with executive, kernel, HAL and kernel-mode drivers. |
| Kernel-level programming interface | Linux system calls, file descriptors, sockets, Binder driver and ioctl/device interfaces; apps normally use framework APIs rather than direct privileged calls. | Mach traps, BSD/POSIX system calls and I/O Kit interfaces; third-party apps generally use public frameworks, not private kernel interfaces. | NT system-service boundary, Win32 subsystem APIs and documented device interfaces; apps use Win32/WinRT rather than calling kernel internals. |
| Runtime environment | Historical Dalvik used DEX bytecode with interpretation and JIT; current Android uses ART with DEX plus install-time AOT and runtime JIT/profile-guided compilation. | Native ARM64 Mach-O executable; Objective-C runtime supplies dynamic class loading, message dispatch and metadata. Swift has its own runtime support. ARC inserts retain/release operations; it is not a tracing garbage collector. | WinRT is an API/platform contract, not a single language runtime. Native apps use PE machine code; .NET apps use CLR/CoreCLR with IL and JIT or AOT depending on deployment. |
| Application framework | Android SDK framework: Activity/Service/Receiver, NotificationManager, JobScheduler/WorkManager, PackageManager and ContentProvider. | UIKit/SwiftUI, UserNotifications, BackgroundTasks and URLSession background transfers. | WinUI/UWP/Windows App SDK and WinRT APIs; background tasks and push notification APIs depend on app model and Windows version. |
| Application isolation | Per-app Linux UID, process sandbox, SELinux policy, permission checks and scoped storage rules. | Per-app sandbox container, entitlements, code signing and mandatory access controls. | AppContainer/package identity and capability declarations for packaged apps; desktop Win32 apps have a different, broader model unless constrained. |
| IPC | Binder is primary framework IPC; also intents, bound services, content providers, sockets and shared memory. | XPC, Mach messages, URL schemes, extensions and shared containers with entitlements. | COM/RPC, WinRT activation, App Services, named pipes and Windows messaging, subject to package/capability boundaries. |
| Background message path | FCM receives push; Google Play services/OS schedules delivery, posts notification or invokes eligible app callback. Doze/app standby defer non-exempt work. Force-stopped apps require user relaunch before normal delivery resumes. | APNs delivers push to the OS. User-visible notification can be presented by the system; eligible background notifications may wake the app briefly, but are discretionary and throttled. User force-quit prevents ordinary background relaunch until the user opens the app. | WNS push channel and system broker deliver toast/raw notifications according to app model and policy; background activation/task execution is constrained by lifecycle and battery policy. |
| Messaging consequence | Use FCM high-priority only for genuinely urgent user-visible events; persist message server-side and fetch after callback. Do not depend on a permanent socket. | Use APNs alert pushes for user-visible arrivals; use background pushes only as best-effort hints, then fetch authoritative content. Do not promise silent background execution. | Use WNS notifications and supported background activation; maintain server-side queue and retry on app activation. Test packaged-app lifecycle separately from classic desktop behaviour. |

**Cross-platform consequence:** The protocol and server queue can be shared, but push registration, permission prompts, background callback, notification presentation and retry logic must be platform adapters. “Message delivered to push service,” “notification shown,” and “message persisted in local inbox” are three different states and must not be treated as equivalent.

## 2.4 Desk-check: screen-off incoming message (1 mark)

**Android path**

1. Radio/network hardware receives packet while screen is off.
2. Modem/Wi-Fi firmware and Linux network driver deliver network traffic through kernel networking.
3. FCM infrastructure and Google Play services receive the push event; Doze policy determines whether/how urgent delivery is allowed.
4. System notification service may post an alert without starting a long-running app process. If an eligible app callback is invoked, Activity Manager starts/uses the app process.
5. Zygote-created process runs ART; framework dispatches the appropriate receiver/service callback.
6. App validates message metadata, fetches encrypted message content over TLS, stores it in encrypted app storage and updates notification/UI state.

**iOS path**

1. Network interface/modem receives traffic; Darwin kernel networking handles device-side network events.
2. APNs service delivers the push to the iOS notification subsystem.
3. For an alert push, the OS can display the notification while the app remains suspended. For an eligible background push, iOS may grant a short execution window.
4. If launched for background handling, the OS creates/resumes the app process and initialises its native executable and Objective-C/Swift runtime.
5. UserNotifications/background callback runs; app fetches authoritative content, verifies it and stores it in its sandbox.
6. User taps the notification; app foreground lifecycle renders the message screen.

## 2.5 Challenge: app process terminated by OS (1 mark)

**Prediction:** Delivery differs in how the app code is reached, but a system-managed alert can still be presented on both platforms. Android can recreate an eligible process for FCM delivery; iOS can present an APNs alert without running the app. Silent/background processing is less guaranteed on iOS. If the user force-stopped Android or force-quit iOS, normal background relaunch is restricted.

**Responsible elements:** Android Activity Manager/FCM/Doze and force-stop state; iOS APNs notification daemon, background-task policy and user force-quit state.

**Relevant trace:** Android: FCM → Play services/system delivery → Activity Manager creates process → ART initialises → eligible callback → fetch/store. iOS alert: APNs → notification daemon → OS displays alert; no app callback is required. On tap: app process launch → runtime initialisation → callback/scene activation → fetch/store.

**Desk-check result:** Prediction is correct with qualification: visible alert delivery can survive process termination, but background application processing is not guaranteed equally. A force-stop/force-quit is a distinct user-controlled condition and must be tested separately.

---

# Task 3 — Runtime Environment Analysis (9 Marks)

## 3.1 Execution model (1 mark)

| Platform | Delivered code | Loader | When executable machine instructions exist |
|---|---|---|---|
| Android (Dalvik-era model) | APK containing DEX bytecode plus resources and native libraries where required. | Package installer registers package; Zygote/Activity Manager starts process; Dalvik VM loads DEX. | Dalvik interpreted DEX and used trace-based JIT in later Dalvik versions; native instructions are produced at runtime for JIT-compiled traces. |
| Android (current ART clarification) | APK/AAB-derived installed package containing DEX and possibly compiled OAT/VDEX artifacts. | Package Manager/ART install-time compiler and app process loader. | AOT portions can be compiled at install/update time; JIT compiles hot code at runtime; execution can use both. |
| iOS (Objective-C runtime) | Signed Mach-O native executable and frameworks, compiled for the target architecture. | dyld dynamic linker/loader, under launch services. | Main app code is native machine code produced ahead of time before installation; dynamic linking and Objective-C method dispatch occur at load/run time, not bytecode-to-native JIT. |
| Windows (WinRT platform) | Packaged PE native binary, or managed .NET assembly containing IL, depending on app technology. | Windows loader; CLR/CoreCLR loads managed assemblies for .NET apps. | Native PE code is already machine code; managed IL is JIT-compiled at runtime or AOT-compiled depending on deployment. WinRT itself is not a bytecode VM. |

## 3.2 Android launch sequence to first screen (2 marks)

| Order | Action and purpose | Component | Required precondition |
|---|---|---|---|
| 1 | User taps app icon; request identifies package and launch activity. | Launcher/Package Manager | App installed and launchable; launcher running. |
| 2 | OS checks package metadata, process state and launch permissions; chooses existing process or new process. | Activity Manager/ActivityTaskManager | Package registration, user profile and system services available. |
| 3 | If cold start, Zygote forks an app process and assigns app UID, process credentials and resource limits. | Zygote/Linux kernel/Activity Manager | Kernel process, memory and scheduler services running; Zygote initialised. |
| 4 | Runtime loads DEX/OAT, verifies classes and initialises ART, heap, class loader and required native libraries. | ART and dynamic linker | Process address space, mapped libraries and runtime image available. |
| 5 | Framework creates Application object and invokes lifecycle initialisation. | Android framework/ActivityThread | ART can execute app code; framework services and Binder are available. |
| 6 | Framework instantiates launch Activity and calls lifecycle callbacks (onCreate, onStart, onResume as appropriate). | ActivityThread/Activity framework | Application initialisation complete; manifest component valid. |
| 7 | App inflates/constructs view hierarchy and submits first frame. | View toolkit, WindowManager, SurfaceFlinger/graphics stack | Activity context, resources, display and graphics services available. |
| 8 | Compositor presents frame on display. | SurfaceFlinger/display HAL/driver | Rendered buffer and display hardware available. |

**Why the sequence matters:** process identity and memory must exist before runtime initialisation; runtime/class loading must exist before framework callbacks can execute app classes; framework/window services must exist before a view can be attached and rendered.

## 3.3 Runtime strategy analysis (4 marks)

**Interpretation, JIT and AOT**

- Interpretation executes bytecode by decoding instructions at runtime. It avoids a full native compilation step but adds repeated dispatch overhead.
- JIT compiles frequently executed bytecode during execution. It can improve hot-path speed but consumes CPU, memory and energy while profiling/compiling.
- AOT compiles code before execution (often at install/build time). It reduces runtime compilation but may increase installation time/storage and can be less adaptive to the current device/workload.

**Android/Dalvik and ART:** Dalvik used DEX bytecode, interpretation and later JIT compilation. Current ART retains DEX as the app distribution format and combines install-time AOT with runtime JIT and profile-guided optimisation. Android apps are managed by a tracing garbage collector; pauses and heap pressure can affect latency, while generational/concurrent techniques reduce but do not eliminate pause cost.

**iOS Objective-C runtime:** App code is native Mach-O produced by AOT compilation. The Objective-C runtime resolves classes, selectors, method dispatch, categories and dynamic metadata. ARC is compiler-assisted reference counting: compiler-inserted retain/release operations manage object lifetime. It avoids a tracing GC pause but reference-count traffic and retain cycles can cost CPU/memory and require careful ownership design. Swift uses ARC for class references too.

**Windows:** WinRT is a set of APIs and activation/metadata contracts, not the language execution engine. Native C/C++ apps use machine code; .NET apps use CLR/CoreCLR with IL and JIT or AOT options. .NET uses a tracing garbage collector; pause/heap costs depend on workload and GC mode.

**Native boundary**

- Android: managed Java/Kotlin → JNI where native code is required → Bionic/native libraries → system calls/Binder → Linux kernel.
- iOS: Objective-C/Swift frameworks and runtime → C/Objective-C ABI and system frameworks → Darwin system-call/Mach interfaces → XNU kernel. Apps use public APIs, not private kernel entry points.
- Windows: WinRT/Win32 API projection or .NET interop → native system DLLs/COM/RPC → NT system-service boundary → Windows kernel.

**Startup, memory, portability**

- Android managed bytecode provides broad device/ABI portability, but runtime, heap and framework loading consume memory; AOT improves repeat startup while JIT adapts hot code.
- iOS native AOT avoids a managed VM/JIT startup stage and can give predictable execution, but binaries are architecture-specific and dynamic runtime metadata still consumes memory.
- Windows varies by app model: native apps avoid managed GC overhead; .NET apps gain language/runtime portability but need CLR and managed heap resources.

**Conclusion for a low-memory device:** A small native AOT application can have the lowest runtime/heap overhead when carefully implemented, so native AOT is the strongest choice under a strict memory budget. However, it sacrifices some portability and requires separate platform builds. If the same codebase must span devices, Android's managed runtime or .NET can be acceptable only with measured heap limits and disciplined background work. There is no universal winner independent of workload and available RAM.

## 3.4 Cold-start and warm-start desk-check (1 mark)

| Step | Cold start | Warm start | Reason |
|---|---|---|---|
| Launcher receives tap | Execute | Execute | User action occurs in both cases. |
| Resolve package/activity | Execute | Execute or reuse cached resolution | OS still validates target. |
| Create process | Execute: Zygote fork | Skip if process remains alive | Warm process already exists. |
| Initialise ART/class loader | Execute substantial initialisation | Reuse initialised runtime | Runtime remains resident in process. |
| Load classes/resources | Load required classes | Reuse loaded classes; load only missing items | Class metadata/cache remains in process. |
| Create Application/Activity | Execute | Recreate Activity if prior Activity destroyed; otherwise resume existing one | Activity lifecycle differs from process lifetime. |
| Build view and render | Execute | Often redraw/resume; may reuse state/view only if retained | Window may need reattachment/redraw. |

A warm start is not guaranteed to reuse an Activity: Android may retain the process but destroy the Activity. If the process was killed, the next launch is cold.

## 3.5 Dependency analysis (1 mark)

The kernel must first provide process creation, virtual address spaces, scheduling, file access and IPC; without these, no application process or runtime heap can exist. ART must then load classes and establish managed execution before framework lifecycle methods can invoke application code. Framework services and Binder endpoints must be available before callbacks can safely request windows, notifications or storage. This dependency order is visible in launch steps 3–7: kernel process → ART initialisation → framework/Application callbacks → Activity/window → rendered frame. Starting a later stage before its dependency would cause unresolved services, invalid memory access or failed launch.

---

# Task 4 — Security Forensics (7 Marks)

## 4.1 Locate the defects (2 marks)

| Original decision | Mechanism bypassed or unused | Why the OS cannot fully protect the user |
|---|---|---|
| Request every permission at install “for future use”. | Least-privilege permission model and runtime consent. | Broad permissions increase the impact of compromise and undermine meaningful user choice. The OS can deny permissions, but cannot make unnecessary access safe once granted. |
| Save login token in a file readable by other apps. | App sandbox, UID isolation and secure storage (Android Keystore + encrypted app-private storage). | If the file is actually shared/world-readable, another app or backup/debug path may obtain the bearer token. OS sandboxing cannot protect data deliberately placed in an accessible location. |
| Accept updates from any source without producer verification. | Package/code signing and trusted update channel. | An attacker can replace executable code or install a malicious update that inherits the app's trust and accesses its data. |
| Use plain unencrypted server connections. | TLS transport protection, server authentication and integrity. | Network observers can read credentials/messages; active attackers can alter or inject traffic. App sandboxing does not protect data in transit. |

## 4.2 Attack scenario (2 marks)

**Scenario:** A malicious app is installed on the same Android phone and the user connects to an attacker-controlled public Wi-Fi access point.

1. SecureNotes has stored its bearer login token in a file accessible outside its private UID sandbox.
2. The malicious app reads that file. **Confidentiality is first lost at this read operation:** the attacker now possesses a reusable authentication token.
3. The user opens SecureNotes over the public network. Because the app uses HTTP/plaintext, the attacker captures notes and session traffic. This is a second confidentiality loss.
4. The attacker modifies a response or injects a fake update download. Since the app accepts updates without verifying the publisher signature, malicious code can be installed or trusted.
5. The attacker uses the stolen token to retrieve or alter account data from another device.

The attack uses at least two independent defects: exposed token storage and absent TLS; unsigned updates can extend the compromise to code integrity.

## 4.3 Minimal repair — Android (2 marks)

| Defective decision | Minimal correction | Android mechanism and architecture location |
|---|---|---|
| Request every permission at install | Declare only required permissions; request dangerous/runtime permissions immediately before the feature needs them; explain purpose and handle denial. | Package Manager and Permission Manager in the framework/system-service layer; enforcement also occurs at framework service/Binder boundaries. |
| Shared token file | Store token only in app-private internal storage; encrypt sensitive token material using a key protected by Android Keystore; never export it to shared storage/logs. | Linux per-app UID sandbox plus framework Keystore service and hardware-backed TEE/StrongBox where available. |
| Unverified updates | Accept updates only from the trusted distribution channel and verify package signing identity/signature; reject mismatched signing certificates. | Package Manager verifies package signatures during install/update; signing identity is part of package trust. |
| Plain HTTP | Require HTTPS with TLS 1.2+ (prefer TLS 1.3 where available), certificate validation and cleartext-traffic prohibition; do not disable validation. | Network Security Configuration/framework networking libraries and TLS native libraries (Conscrypt/BoringSSL depending on build), below app code. |

## 4.4 Regression check (1 mark)

**Legitimate behaviour:** The user chooses “Attach contact” and grants Contacts permission.

**Regression trace:** app requests Contacts permission only when the feature is invoked → Permission Manager displays consent → user grants → app queries Contacts Provider through its framework API → provider checks caller UID/permission → app receives permitted contact fields → contact is attached and transmitted over TLS. If denied, the app still supports manual entry. Token storage remains private and update-signature verification does not interfere with contact selection. Thus the legitimate consent-based behaviour is preserved.

---

# Task 5 — Power Management Reasoning (7 Marks)

## 5.1 Power-state policy (3 marks)

| State | Hardware/kernel behaviour | Entry condition | Exit condition | Permitted work |
|---|---|---|---|---|
| ACTIVE | CPU clocks and display may run at performance levels; scheduler runs foreground threads; sensors enabled only as needed. | User interaction, active workout screen, explicit short sensor sampling window or urgent event. | Screen idle, no immediate work, user leaves screen or sampling window ends. | Foreground UI; short sensor reads; bounded network/storage tasks. |
| IDLE | Display off/dim; CPU enters low-power idle states; kernel coalesces timers; radios use low-power modes; nonurgent jobs deferred. | No user input for configured timeout and no foreground-critical work. | User input, sensor threshold event, scheduled maintenance window or push event. | OS services, batched jobs, permitted sensor batching; no continuous app polling. |
| SUSPENDED | Most CPU execution stops; RAM retained in low-power state; wake sources remain armed; modem may use network paging/low-power radio. | Idle timeout and no active wake lock or critical kernel activity. | Hardware wake interrupt, alarm, incoming push wake event or power-button/user input. | Only kernel/firmware wake handling and OS-authorised brief work after resume. |

**Fitness sensor policy:** use hardware sensor batching/FIFO and threshold-triggered delivery; request a wake lock only for the short interval needed to drain a batch or persist a critical reading. Record timestamps and sequence numbers so a delayed batch does not lose sample ordering.

## 5.2 Urgent push while suspended (2 marks)

The insufficient part is the assumption that an application must keep the processor permanently awake to receive every event. That prevents entry into SUSPENDED and wastes energy. Use the platform push service (for example FCM) and hardware/network wake signalling: the modem/OS wakes the device, the system receives the push, and the OS grants a short execution window or displays the notification. Use WorkManager/JobScheduler for deferred follow-up; use a partial wake lock only for a bounded, user-visible critical operation.

The app must stop polling the network continuously, holding a permanent wake lock and treating every sensor sample as requiring immediate CPU execution. Sensor FIFO/batching and push-based wake-up preserve urgent notification while allowing sleep.

## 5.3 Battery saver at 15% (2 marks)

| Level | Change when battery ≤15% and saver enabled |
|---|---|
| Kernel/hardware | Reduce CPU frequency/performance hints; prefer deeper idle states; restrict nonessential wakeups and background scheduling; reduce display refresh/brightness through power policy; retain wake sources required for emergency/system functions. |
| Runtime/system services | Defer background jobs, increase batching/coalescing, limit background network and location work, reduce process priority for nonessential work; do not disable correctness-critical storage or security services. |
| Application | Reduce sensor sampling frequency where medically/operationally acceptable; use sensor FIFO; pause animations and nonessential sync; compress/batch uploads; keep urgent safety alerts enabled. Persist data before deferred work. |

**Trade-off:** dashboard updates may appear less frequently and cloud synchronisation may be delayed. This is acceptable because local timestamped records remain durable and urgent alerts remain enabled, while the ten-hour shift battery target is prioritised.

---

# Task 6 — Design Challenge: RuralCare Field-Data System (13 Marks)

## Stage 1 — Interpret the problem (2 marks)

| Element | Definition |
|---|---|
| Input | Patient observations/forms, worker identity, device class, connectivity state, battery state, security capabilities and server acknowledgements. |
| Output | Correctly stored local records and a server dataset with each record synchronised exactly once logically, even if transport retries occur. |
| Objective | Enable offline data collection for hours, protect patient data on a lost device and complete a ten-hour shift on one charge across three device classes. |
| Constraints | Android/iOS modern security and background controls; Class C may have only J2ME or WML, small memory, limited crypto/storage APIs and intermittent/slow networks; no data loss or duplicate logical records; battery budget. |
| Decisions | Native vs shared UI; whether Class C can store sensitive data; local encryption/key strategy; sync protocol; push/background strategy; battery thresholds; lost-device response. |

## Stage 2 — Platform strategy (2 marks)

**Selected strategy: native applications for Class A and B, plus a capability-gated J2ME client for Class C; WML is a restricted fallback only for non-sensitive online tasks.**

- **Class A Android:** Native Android app uses Room/SQLite in app-private storage, Android Keystore-backed encryption, WorkManager/JobScheduler and FCM. Native integration gives access to UID sandbox, Keystore, sensor batching and power APIs.
- **Class B iPhone:** Native iOS app uses encrypted Core Data/SQLite storage with file protection and Keychain, APNs, BackgroundTasks and background URLSession. Native integration respects iOS suspension and data-protection rules.
- **Class C J2ME:** A J2ME client may capture and queue offline records only on a qualified device whose implementation provides a vetted cryptographic facility (for example SATSA or a vendor-provided secure element/crypto API), protected local key handling and sufficient persistent RMS storage. Because generic J2ME/WML does not guarantee hardware-backed secure storage or a standard modern keystore, every model must pass a security qualification before patient data is enabled.
- **WML:** Use only for online, non-sensitive workflow/status pages. A WML browser is not a reliable offline encrypted patient-record store and therefore cannot meet the offline PHI requirement by itself.
- **Fail-closed rule:** If a Class C model cannot protect locally stored patient data with an approved cryptographic key, it must not store identifiable patient records offline. It can collect only non-identifying task codes or must be replaced with a qualified device. This is a capability limitation, not a claim that all feature phones are secure.

A shared backend schema and sync protocol are used across all clients; platform-specific storage, encryption, notification and lifecycle adapters remain native.

## Stage 3 — Critical information and constraints (2 marks)

| Class | Runtime environment | Security mechanisms | Power controls | Offline storage | Connectivity |
|---|---|---|---|---|---|
| A Android smartphone | ART for Java/Kotlin; Android framework. | App UID sandbox, SELinux, runtime permissions, Android Keystore, package signing, TLS. | Doze, App Standby, JobScheduler/WorkManager, sensor batching, bounded wake locks, Battery Saver. | Encrypted Room/SQLite in internal app storage; Keystore-wrapped data key. | Wi-Fi, LTE/5G; intermittent; FCM push; HTTPS sync. |
| B iPhone | Native ARM64; Objective-C/Swift runtime and iOS frameworks. | App sandbox, code signing/entitlements, Keychain, Data Protection classes, TLS. | App suspension, BackgroundTasks, background URLSession, APNs; no general permanent background execution. | Encrypted Core Data/SQLite; file protection; Keychain-protected key. | Wi-Fi, LTE/5G; APNs; HTTPS sync. |
| C feature phone | J2ME/CLDC MIDlet runtime or WML browser; vendor-dependent. | MIDlet permissions/signing vary; optional SATSA/secure element; no universal keystore or sandbox guarantee. | Limited control; avoid polling; batch writes and radio sessions; device-specific sleep behaviour. | RMS record store; encrypt records only if approved crypto/key facility is present. WML has no dependable offline PHI store. | 2G/feature-phone data/SMS depending on model; low bandwidth and long outages. |

**Information retained for safe synchronisation**

1. Globally unique record ID (UUID or server-issued namespace + device-generated random ID): identifies the logical record across retries.
2. Patient pseudonymous identifier and form/schema version: binds data to the correct patient and interpretation.
3. Device ID, worker ID and shift/session ID: provenance and audit attribution.
4. Monotonic local sequence number: preserves capture order and detects gaps.
5. Client-created timestamp plus timezone/clock-quality indicator: supports chronology without trusting an inaccurate device clock.
6. Payload hash and schema version: detects corruption and incompatible versions.
7. Encryption/key version and authentication tag: permits integrity verification and key rotation.
8. Sync state (pending/in-flight/acknowledged) and attempt metadata: supports restart after interruption.
9. Server acknowledgement containing record ID and committed version: prevents duplicate logical inserts.
10. Conflict/version metadata: resolves edits without silently overwriting newer data.

## Stage 4 — Complete solution specification (4 marks)

### 4.1 Logical architecture

`Capture UI → Validation → Local Record Service → Encryption → Durable Offline Queue → Sync Coordinator → TLS API Gateway → Authentication/Authorisation → Idempotent Record Service → Encrypted Database → Acknowledgement`

- **Device layer:** sensors/forms and local UI.
- **Application layer:** validation, patient/worker context, queue management and conflict policy.
- **Platform layer:** ART/iOS native runtime/J2ME; lifecycle, permissions, secure key APIs and scheduling.
- **Storage layer:** encrypted database/RMS with integrity metadata.
- **Transport layer:** TLS-protected HTTPS API; authenticated device session; retry-safe request IDs.
- **Server layer:** authentication, authorisation, schema validation, idempotency ledger, audit log, encrypted database and backup.

### 4.2 Data capture and offline storage

1. Authenticate worker at shift start; unlock local data key using platform-protected credential.
2. Create a record with UUID, patient pseudonymous ID, worker/device/shift IDs, schema version, sequence number and timestamp.
3. Validate required fields and range constraints before accepting the record.
4. Canonicalise payload; calculate integrity hash; encrypt payload with an AES-GCM data key. Store nonce, ciphertext, authentication tag and key version.
5. Store encrypted envelope and sync metadata in a transaction. Mark record PENDING only after durable commit succeeds.
6. UI displays “Saved on device — pending sync”; never label it “synced” until server acknowledgement is verified.
7. Keep keys outside the database: Android Keystore, iOS Keychain/Secure Enclave-backed protection where available; Class C uses only an approved secure-element/vendor key facility. Do not store raw key beside ciphertext.

### 4.3 Security and lost-device behaviour

- **At rest:** per-device data key, encrypted record payloads, app-private storage, authenticated encryption, screen lock and platform data protection. Minimise locally retained patient fields.
- **In transit:** TLS with server certificate validation; mutual device authentication where practical; short-lived access tokens; token rotation; no credentials in logs.
- **Authorisation:** server checks worker role, organisation, patient assignment and device registration for every upload/download.
- **Lost device:** worker reports loss; server revokes device credentials and refresh tokens; remote wipe is attempted where supported but is not relied upon; local keys are protected by device unlock and platform keystore; next sync rejects revoked device. Keep audit trail.
- **Class C limitation:** if device lacks a protected key facility, do not store identifiable patient data offline. A WML-only client is online-only and may not cache PHI.

### 4.4 Power policy for a ten-hour shift

- At shift start, perform one authentication and configuration sync.
- During offline collection, keep screen off between forms; use low-power sensor sampling and event-driven capture; persist each completed record transactionally.
- Do not maintain an always-on socket or permanent wake lock.
- Sync in batches when connectivity is available and battery is above 20%; at or below 20%, defer nonurgent uploads but retain local data.
- At 15%, enter field battery-saver: reduce screen brightness, disable animations, batch sync and lower noncritical sampling. Keep emergency functions and durable local writes active.
- Use OS scheduler/push for wake-up; on Class C use manual/periodic worker-initiated sync to avoid radio polling.

### 4.5 Synchronisation protocol (ordered and interruption-safe)

1. Client detects connectivity and policy permits sync.
2. Client obtains a short-lived authenticated session and requests server sync cursor.
3. Client selects PENDING records in sequence order and forms a bounded batch.
4. Client sends batch over TLS with a stable idempotency key per record.
5. Server authenticates device/worker, validates schema and permissions, verifies payload integrity, and checks idempotency ledger.
6. For a new UUID, server commits record and ledger entry in one database transaction. For an existing UUID with same hash, server returns the previous acknowledgement without inserting a duplicate. Same UUID with different hash is quarantined as a conflict.
7. Server returns per-record ACKs with UUID, hash and committed version.
8. Client verifies each ACK; only acknowledged matching records become SYNCED. Unacknowledged records remain PENDING.
9. If connection drops at any point, client retains unacknowledged records and retries the same UUID/idempotency key. It never generates a new UUID for a retry.
10. On next session, client asks for ACK status/cursor and resumes from the first unacknowledged sequence. Conflicts enter a review queue; no silent last-write-wins for clinical records.

### 4.6 Failure handling by class

| Class | Failure | Required behaviour |
|---|---|---|
| A | OS kills process or enters Doze | Transactional queue survives process death; WorkManager/FCM schedules later sync; app resumes from persisted ACK state. |
| A | Keystore key unavailable before first unlock | Do not expose/decrypt PHI; ask authorised user to unlock; preserve ciphertext. |
| B | App suspended or terminated | Persist before background exit; use background URLSession/BackgroundTasks where granted; retry on foreground launch. |
| B | Data Protection file unavailable while locked | Defer read/write until permitted unlock; do not weaken file protection to force background access. |
| C J2ME | Low memory or MIDlet termination | Commit each record atomically to RMS; recover pending queue on next start; show storage-full warning before accepting another record. |
| C J2ME | No SATSA/approved crypto | Disable PHI offline mode; do not write identifiable records. |
| C WML | Network disappears | Preserve no PHI in browser cache; show offline-unavailable state and direct worker to qualified offline-capable device. |
| All | Interrupted sync | Retain pending UUIDs and repeat idempotent upload; ACK only after verified server commit. |
| All | Device reported lost | Revoke server credentials; reject future sync from device; rely on encrypted local storage and protected keys, not remote wipe alone. |

## Stage 5 — Desk-check: Class A offline six hours, battery 20%, then lost (1 mark)

1. Worker signs in; Android creates protected app session and Keystore-backed data key.
2. Network becomes unavailable. Sync coordinator records OFFLINE state; capture continues locally.
3. For six hours, each patient record is validated, encrypted and committed to the local queue with a unique UUID and sequence number. Status remains PENDING.
4. Battery falls to 20%. Policy disables nonurgent sync attempts and reduces screen/sensor activity; no record is deleted.
5. Device is lost before any sync. Worker reports loss; administrator revokes device tokens and server rejects future requests from that device.
6. **Exposed:** only metadata visible outside encrypted storage, such as app/package presence and possibly unencrypted operational metadata deliberately retained. With a locked device and protected key, patient payload ciphertext should not be intelligible.
7. **Lost:** no server copy exists for the six hours of pending records. If the device is physically destroyed or its protected key becomes unrecoverable, those unsynchronised records may be permanently lost.
8. **Recoverable:** server can recover records acknowledged before loss (none in this scenario); local pending records are recoverable only if the device and protected key are recovered and authorised access remains possible.

**Interpretation:** confidentiality is protected by encryption/key isolation; availability is not guaranteed for never-synchronised data. The design makes this residual risk explicit and requires workers to report loss immediately.

## Stage 6 — Attack the design (2 marks)

| Adverse condition | Why challenging | Prediction | Trace/result | Required decision/refinement |
|---|---|---|---|---|
| 1. Stolen unlocked Android phone | Attacker may use an active app session and read decrypted screens even if database is encrypted. | Encryption at rest alone may not stop an attacker while the app is unlocked. | App auto-lock timeout, re-authentication for patient export, screen privacy and server token revocation limit access; however data visible during the active unlocked session remains exposed. | Critical decision is short session lock and least-privilege UI. Add immediate app lock after inactivity and re-authentication for bulk export. |
| 2. Sync connection drops after server commit but before ACK reaches client | Client cannot know whether server committed; naïve retry may duplicate records. | Idempotency ledger will prevent a second logical insert. | Retry uses same UUID/hash; server finds committed ledger entry and returns same ACK; client marks SYNCED. | Atomic record+ledger transaction and stable UUID are critical. If ledger is not atomic, duplicate risk remains; enforce transaction and unique constraint. |
| 3. Class C model has no secure storage or approved cryptographic API | RMS may be readable after device loss; key stored beside ciphertext is recoverable. | Fail-closed policy should prevent identifiable offline data from being collected on that model. | Capability check fails at enrolment; PHI offline mode disabled; WML mode cannot cache PHI. Requirement is met only by assigning a qualified device. | The device qualification gate is critical. If organisation insists on offline PHI on an unqualified device, the security requirement cannot be met; replace device or add approved secure hardware. |
| 4. Device clock is wrong and records arrive out of order | Timestamp-based merge could reorder events or overwrite newer data. | Sequence numbers and server receipt metadata preserve capture order independently of wall clock. | Server stores client timestamp as evidence but orders within device/shift by sequence; conflicts are flagged. | Retain monotonic sequence and clock-quality flag; do not use client wall clock as sole authority. |

**Overall conclusion:** The architecture meets offline durability and duplicate prevention when local commits are transactional and sync is idempotent. Lost-device confidentiality depends on key protection and device lock. Generic J2ME/WML capability is not sufficient by assumption; unsupported Class C models must be excluded from offline identifiable-data collection. The ten-hour target is a measurable acceptance test on each qualified device model, not something architecture alone can guarantee.

---

# Submission conclusion

The design separates kernel, runtime, framework, application, storage and transport responsibilities. It distinguishes push delivery from app execution, bytecode from native code, and encrypted local persistence from confirmed server synchronisation. Each major decision has a trace or failure test. Device-specific capability checks are mandatory, especially for legacy feature phones.
