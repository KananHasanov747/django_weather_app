FROM nginx:stable-alpine

RUN apk add --no-cache fail2ban

COPY fail2ban/jail.local /etc/fail2ban/

RUN fail2ban-client start
