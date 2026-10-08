## How they are classified

**1. By material system**
- GaAs-based
- InP-based
- GaN-based
- Antimonides (GaSb)
- Quantum cascade lasers

**2. By where the light exits**
- Edge-emitting lasers (EEL)
- VCSELs

**3. By cavity and wavelength control**
- Fabry-Pérot
- DFB
- DBR and tunable
- EML

**4. By active region**
- Bulk
- Quantum well
- Quantum dot

**5. By integration**
- Discrete chips
- Monolithic InP PICs
- Heterogeneous III-V on Si / SiN
- Epitaxial growth on Si

## Datacenter use

**Today**
- Short reach (multimode): 850 nm GaAs VCSELs
- Single-mode (500 m–2 km+): InP EMLs, InP CW DFB + silicon photonics

**Trend outlook**
- InP CW DFB as external laser source for co-packaged optics
- Heterogeneous III-V on Si / SiN
- Quantum-dot lasers
- Multi-wavelength comb lasers





# III-V Semiconductor Lasers

**III-V semiconductor lasers** are laser diodes made from compounds of group III elements (gallium, indium, aluminium) and group V elements (arsenic, phosphorus, nitrogen, antimony). Silicon and germanium can't lase efficiently because they have an indirect bandgap. III-V compounds have a direct bandgap, so electrons and holes recombine and emit light efficiently. That's why nearly every laser in optical communication is III-V. Even silicon photonics still needs III-V material for the light source: compared with germanium-based lasers, III-V lasers need less power and give a cleaner single-wavelength output.

## How they are classified

### 1. By material system (decides the wavelength)

- **GaAs-based** (AlGaAs, InGaAs on GaAs): about 780–1060 nm. Used for VCSELs, pump lasers and sensing.
- **InP-based** (InGaAsP, InAlGaAs on InP): about 1260–1650 nm, the O-band and C-band used in fibre. This is the workhorse for telecom and single-mode datacom.
- **GaN-based** (InGaN): blue, violet and green. Used in displays, Blu-ray and lighting, not datacom.
- **Antimonides** (GaSb) and **quantum cascade lasers**: mid-infrared, used for gas sensing.

### 2. By where the light exits

- **Edge-emitting lasers (EEL):** light comes out of the cleaved side of the chip. They give higher power and suit long distances.
- **VCSELs (vertical-cavity surface-emitting lasers):** light comes out of the top surface. They are cheap, can be tested on the wafer, and come in arrays, but have lower power and mostly operate at 850 nm.

### 3. By cavity and wavelength control

- **Fabry-Pérot:** emits several wavelengths at once. Cheap.
- **DFB (distributed feedback):** a grating inside gives one clean wavelength. This is the standard for single-mode links.
- **DBR and tunable lasers:** wavelength can be adjusted. Used in coherent and DWDM systems.
- **EML (electro-absorption modulated laser):** a DFB laser with a modulator on the same chip, used for high data rates.

### 4. By active region

Bulk, quantum well (the current standard), and quantum dot. Quantum-dot lasers tolerate heat and crystal defects better, which makes them attractive for growing directly on silicon.

### 5. By how they are integrated with other chips

Discrete chips, monolithic InP photonic integrated circuits (PICs), heterogeneous integration (III-V bonded onto silicon or silicon nitride), and epitaxial growth directly on silicon (still mostly research).

## Which is used in datacenters, and what wins next

Today, the choice depends on distance:

- **Short links (up to about 100 m, multimode fibre):** 850 nm GaAs VCSELs. They're the cheapest option, but reaching higher speeds is getting harder.
- **Up to about 2 km and beyond (single-mode fibre):** InP lasers. These are either EMLs, or continuous-wave (CW) DFB lasers that feed silicon-photonics modulators. The 800G and 1.6T transceivers in AI clusters mostly use one of these two.

For the next few years, **InP is the strongest bet**, specifically high-power, very reliable CW InP DFB lasers. The industry is moving to **co-packaged optics (CPO)**, where the optics sit right next to the switch or GPU chip. There, the laser is often kept separate as an *external laser source*. This is because lasers are the part most sensitive to heat and most likely to fail, so it helps to be able to replace them. Watch these trends:

- **Heterogeneous III-V on silicon or silicon nitride:** the laser is built directly into the photonic chip.
- **Quantum-dot lasers:** better at high temperature, and promising for growth on silicon.
- **Multi-wavelength comb lasers:** one source produces many WDM channels.

VCSELs will stay in short-reach links, but there's no single "best" laser. For the AI datacenter build-out, InP lasers designed for CPO and silicon photonics are where the investment is going.