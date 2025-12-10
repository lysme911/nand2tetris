vmtranslator.py  →  主程式，呼叫 Parser 讀取 .vm，再呼叫 CodeWriter 產生 .asm
       ↓
vmparser.py      →  專門負責解析 VM 文字，拆成 commandType, arg1, arg2
       ↓
vmcodewriter.py  →  將 Parser 解析好的資料產生對應的 Hack Assembly

##
把要的vm檔放進同個資料夾，cd到資料夾後打python vmtranslator.py xxx.vm
會產生對應的xxx.asm，放到原本vm檔在的資料夾，之後開cpu emulator檢查output是否一樣