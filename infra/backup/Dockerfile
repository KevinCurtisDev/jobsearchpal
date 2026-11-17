# Nightly encrypted off-site PostgreSQL backups for the Tier 0 beta box.
FROM postgres:16-alpine
RUN apk add --no-cache aws-cli gnupg tzdata
ENV TZ=Europe/Dublin
COPY backup.sh restore-test.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/backup.sh /usr/local/bin/restore-test.sh \
 && echo "30 2 * * * /usr/local/bin/backup.sh >> /proc/1/fd/1 2>&1" > /etc/crontabs/root \
 && echo "15 4 * * 0 /usr/local/bin/restore-test.sh >> /proc/1/fd/1 2>&1" >> /etc/crontabs/root
CMD ["crond", "-f", "-l", "8"]
