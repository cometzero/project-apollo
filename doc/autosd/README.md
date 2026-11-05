# AutoSD 문서

- [Yocto 커널 RPM 및 Automotive AIB 전환 계획](automotive-rpm-aib-migration-plan-ko.md):
  Yocto 커널·모듈 바이너리를 RPM으로 패키징하고 AIB 완성 이미지를 실행하는 계획.
  새 진입점은 `build_autosd.sh`, 기본은 Automotive이며 minimal QM을 옵션으로 선택한다.
- [현재 전체 빌드·실행 Quick Guide](../autosd-minimal-qm-build-ko.md):
  현재 구현의 실행 절차. 위 계획이 구현되기 전까지 이 가이드가 실행 기준이다.
- [현재 Yocto 커널 RPM 전환 검증](automotive-source-build-validation-20261105-ko.md):
  실제 빌드·부팅 완료 여부와 남은 항목.
- [Native AIB 검증 결과](../autosd-native-builder-20261102-ko.md)
- [Native 이미지 QBox 부팅 검증 결과](../autosd-native-boot-20261102-ko.md)
- [Dashboard 문서](../dashboard/README.md)

계획 문서와 완료된 구현·실행 검증 결과를 구분한다.
