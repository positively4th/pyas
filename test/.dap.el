(dap-register-debug-template "test_pyas"
  (list :type "python"
        :args ""
        :cwd (expand-file-name "~/projects/pyas")
        :env '(("PYTHONPATH" . "."))
        :target-module "test/test_pyas.py"
        :request "launch"
        :name "test_pyas"))
