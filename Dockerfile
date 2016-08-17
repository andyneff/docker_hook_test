FROM debian:jessie

ARG TEST=111

ADD pwd_file build.files build.env /

CMD ["bash"]