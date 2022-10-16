(dap-register-debug-template "test_pyas"
  (list :type "python"
        :args ""
        :cwd (expand-file-name "~/projects/pyas")
        :env '(("PYTHONPATH" . "."))
        :target-module "test/test_pyas.py"
        :request "launch"
        :name "test_pyas"))

(dap-register-debug-template "test_pyas_v2"
  (list :type "python"
        :args ""
        :cwd (expand-file-name "~/projects/pyas")
        :env '(("PYTHONPATH" . "/src"))
        :target-module "test/test_pyas_v2.py"
        :request "launch"
        :name "test_pyas_v2"))
