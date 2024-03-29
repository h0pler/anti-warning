# anti-warning  
프록시를 사용해서, 차단된 사이트에 접속이 가능하도록 하는 웹 서비스입니다.  
선린인터넷고등학교 서버 프로그래밍 전공동아리 TeamLog의 2023 겨울 프로젝트로부터 시작되었습니다.  
#### version-231202
기본적인 기능들은 모두 작동하지만,  
아직도 고쳐야 할 문제들이 많습니다.

## 작동 방식  
웹 스크래핑을 통해 유효한 프록시 서버들을 찾은 후,  
서버에 접속한 사용자의 요청을 랜덤한 프록시 서버로 포워딩합니다.  


## 사용  

### PIP 패키지 설치  
아래 명령어를 통해 코드 실행에 파이썬 의존성들을 설치할 수 있습니다.  
```bash
pip install -r requirements.txt
```  
### 코드 실행
아래 명령어를 통해 코드를 실행할 수 있습니다.  
```bash
python3 main.py 
```

---
---

##### 개선점
- 코드 리팩터링  
- 알고리즘 개선  
- 모듈화 구조 개선  
- 비동기 / 멀티스레딩 개선  
- 구현하지 못한 기능들 구현  