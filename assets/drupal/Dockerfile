FROM uspdev/uspdev-php-apache:latest

RUN sed -i 's|/var/www/html|/var/www/html/web|' /etc/apache2/sites-available/000-default.conf

# composer
USER www-data
COPY --chown=www-data . .
RUN composer install

CMD ["apache2-foreground"]