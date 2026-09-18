import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import backend.app as a
print(sorted({r.path for r in a.app.routes if hasattr(r, 'path')}))
