Trigger efficiency with a BNN
------------------------------------------------
Sam Bein adapated from Harrison Prosper adapted from Radford Neal
Created: 25-Mar-2014  

This is a repo of a recently re-discovered application for estimating the trigger efficiency with a BNN.  The following is mostly Harrison's original README but edited/prepared with the example of the CMS RUn 2 MET/MHT trigger family (HLT_PFMETX_PFMHTX*_v*). It requires you to prepare a text file (.dat) with rows for the feature vectors for events that pass the given trigger, and another .dat file for events that faile the trigger. The training uses a classificaiton trick to return an ensemble of estimates of the trigger efficiency; the writer then produces a cpp function that returns the median and quantiles of this ensemble, which you can use as an event weight+uncertainty in your analysis. 

Introduction
------------
The file `doc/BNN.pdf` in this directory provides a terse introduction to the Bayesian Neural Network (BNN) package by Radford Neal.  
His software can be found (if still available) at:

    http://www.cs.toronto.edu/~radford/software-online.html

**Notes on Neal’s Package**  
1. It was used in key analyses (e.g., first single top evidence in 2006; H→ZZ→4ℓ).  
2. Once compiled, it “remembers” its installation path. If you move or rename its folder, you must recompile.  
3. It uses plain-text files for inputs/outputs.  
4. It **cannot** handle weighted events. If your data are weighted, you must create an unweighted sample first.

The workflow below is tailored to measuring the efficiency (and associated uncertainty) of MET-based triggers (e.g., HLT_PFMET100_PFMHT100, etc.) in CMS Run 2 searches for dark matter / SUSY.

To compile the Neal package
---------------------------
    cd fbm.2004-11-10
    ./make-clean
    ./make-all

After compilation, ensure the executables (`net-spec`, `net-mc`, `net-display`, etc.) are in your `$PATH`. For example:

    export PATH=/full/path/to/fbm.2004-11-10/bin:$PATH

Setup
-----
1. **Edit `setup.sh`** (if it exists) and source it, or manually set the PATH as shown above.  

2. **Data**  
   Suppose you have two text files containing unweighted events:

trigdatafiles/passTrigger_MetMhtSextet.dat trigdatafiles/failTrigger_MetMhtSextet.dat

Each file has columns for the input variables, plus a final column indicating pass/fail as 1/0.  
- If your data were originally weighted, first convert them by sampling with replacement. For example:

      python bin/unweight.py passWeighted.dat passTrigger_MetMhtSextet.dat 20000
      python bin/unweight.py failWeighted.dat failTrigger_MetMhtSextet.dat 20000

3. **Randomly mix pass & fail, scale variables**  
The script `mixsigbkg.py` does the following:
- Reads pass/fail `.dat` files  
- Merges them into a single training file  
- Optionally scales each variable to mean=0, std=1  
- Outputs `<NAME>.dat` and `<NAME>.var`

For a “real MET” example named `MetMhtSextet`, run:

    python bin/mixsigbkg.py MetMhtSextet
    
This expects:
- `passTrigger_MetMhtSextet.dat`  
- `failTrigger_MetMhtSextet.dat`

It produces:
- `MetMhtSextet.dat` (mixed, possibly scaled)  
- `MetMhtSextet.var` (offset/scale for each variable)

The last column in `MetMhtSextet.dat` is the target: 1 (pass) or 0 (fail).

4. **Create training script**  
To generate a `.sh` that runs Neal’s posterior density sampler, use `mktrain.py`. For example:

    python bin/mktrain.py MetMhtSextet

This outputs `MetMhtSextet.sh` with commands to call `net-spec`, `net-mc`, etc. You can customize the command-line options (e.g. `-mb` for binary classification, `-N` for number of events, `-H` for hidden nodes, `-I` for MCMC iterations, etc.).

Construct the BNN
-----------------
1. **Run the Hybrid Monte Carlo**  
Launch the sampling by sourcing the generated script in the background:

    source MetMhtSextet.sh &

This runs Neal’s HMC, which saves neural network parameters at each iteration to `MetMhtSextet.bin`.  
Periodically check progress:

    net-display -h MetMhtSextet.bin

The integer “index” shows which iteration of the chain you’re on.

2. **Write out a self-contained C++ function**  
When you’re satisfied the chain has converged (i.e., enough iterations), produce a C++ function representing the trained BNN:

    python bin/netwrite.py -n200 MetMhtSextet.bin
    
This reads the last 200 samples from the Markov Chain, averages them, and writes `MetMhtSextet.cpp`. The `.var` file’s scaling parameters are embedded in that C++ code. You can compile `MetMhtSextet.cpp` in your analysis or just treat it as a reference.

3. **Monitor or finalize**  
You can again inspect the `.bin` with:

    net-display -h MetMhtSextet.bin
    
to ensure it has enough samples.

Test
----
For a quick distribution plot or performance check, you can adapt a script such as `plotBNN.py` to read the `.bin` or the `.cpp` function. For instance:

 python plotBNN.py MetMhtSextet.bin

This will show how the BNN output separates pass vs. fail events.

---

Example Command Flow
--------------------
Below is a condensed list of commands for the *real MET (MetMhtSextet)* example:

1. **Mix pass/fail data**  

    python bin/mixsigbkg.py MetMhtSextet
    
Produces `MetMhtSextet.dat` and `MetMhtSextet.var`.

2. **Create a training shell**  

    python bin/mktrain.py MetMhtSextet
    
Produces `MetMhtSextet.sh`.

3. **Run the MCMC**  

    source MetMhtSextet.sh &
    
Writes networks to `MetMhtSextet.bin`.

4. **Check chain**  

    net-display -h MetMhtSextet.bin

5. **Write final C++**  

    python bin/netwrite.py -n200 MetMhtSextet.bin
    
Produces `MetMhtSextet.cpp`.

Afterwards, you can compile and link `MetMhtSextet.cpp` into your analysis software or just parse the `.bin` directly for posterior predictions.

---

Enjoy using Bayesian Neural Networks for MET/MHT trigger studies!  
For detailed documentation, see the original `doc/BNN.pdf` or Radford Neal’s website.  

