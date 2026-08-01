# Tien xu ly dataset qua preprocess_dataset.py cua repo.
# Env: QRD_DATASET (mac dinh PhysionetMI), ENSEMBLE_MI_DIR
# Chay TUNG subject, bo qua file da co, loi 1 subject khong lam chet ca job.
import os, sys, time
sys.dont_write_bytecode = True
REPO = os.environ["ENSEMBLE_MI_DIR"]
os.chdir(REPO); sys.path.insert(0, REPO)
sys.argv = ["preprocess_dataset.py"]        # BAT BUOC: create_exp_args tu parse sys.argv

DS = os.environ.get("QRD_DATASET", "PhysionetMI")
from src.config import get_subject_list
import preprocess_dataset as P

outdir = os.path.join("preprocessed_data", DS)
allsub = get_subject_list(DS)
todo = [s for s in allsub
        if not os.path.exists(os.path.join(outdir, "windows_dataset_%03d.pkl" % s))]
print("dataset=%s | tong=%d | con thieu=%d -> %s" % (DS, len(allsub), len(todo), todo), flush=True)

ok, fail, t0 = [], [], time.time()
for i, s in enumerate(todo, 1):
    os.environ["QRD_ONLY_SUBJ"] = str(s)
    try:
        t1 = time.time()
        P.main(P.exp_args_dict)
        ok.append(s)
        print("[%d/%d] subject %03d OK (%.1fs)" % (i, len(todo), s, time.time()-t1), flush=True)
    except Exception as e:
        fail.append(s)
        print("[%d/%d] subject %03d LOI: %r" % (i, len(todo), s, e), flush=True)
        import traceback; traceback.print_exc()

print("\nXONG %.1f phut | thanh cong=%d | that bai=%d %s"
      % ((time.time()-t0)/60, len(ok), len(fail), fail), flush=True)
