# Use a imagem oficial do MinIO como base
FROM minio/minio

# Defina variáveis de ambiente padrão (opcional)
ENV MINIO_ROOT_USER=agenda
ENV MINIO_ROOT_PASSWORD=agenda@2024

# Crie o diretório de configuração e copie o arquivo de configuração personalizado
RUN mkdir -p /root/.minio
COPY config.json /root/.minio/config.json

# Comando para iniciar o MinIO
ENTRYPOINT ["minio"]
CMD ["server", "/data"]
