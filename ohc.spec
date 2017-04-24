%{?scl:%scl_package ohc}
%{!?scl:%global pkg_name %{name}}

Name:		%{?scl_prefix}ohc
Version:	0.6.1
Release:	2%{?dist}
Summary:	Java large off heap cache
License:	ASL 2.0
URL:		http://caffinitas.org/
Source0:	https://github.com/snazy/%{pkg_name}/archive/%{version}.tar.gz

BuildRequires:	%{?scl_prefix_maven}maven-local
BuildRequires:	%{?scl_prefix_maven}jna
BuildRequires:	%{?scl_prefix_maven}maven-plugin-bundle
BuildRequires:	%{?scl_prefix_maven}testng
BuildRequires:	%{?scl_prefix_maven}maven-source-plugin
BuildRequires:	%{?scl_prefix}guava
BuildRequires:	%{?scl_prefix_java_common}apache-commons-cli
BuildRequires:	%{?scl_prefix}log4j
BuildRequires:	%{?scl_prefix}log4j-slf4j
BuildRequires:	%{?scl_prefix}metrics
BuildRequires:	%{?scl_prefix}lz4-java
BuildRequires:	%{?scl_prefix}apache-commons-math
BuildRequires:	%{?scl_prefix}jmh
BuildRequires:	%{?scl_prefix}jmh-generator-annprocess
BuildRequires:	%{?scl_prefix}snappy-java
BuildRequires:	%{?scl_prefix_maven}exec-maven-plugin
BuildRequires:	%{?scl_prefix_maven}maven-surefire-plugin
# transitive need to be added for scl
BuildRequires:	%{?scl_prefix}disruptor
BuildRequires:	%{?scl_prefix}jctools
BuildRequires:	%{?scl_prefix}jackson-core
BuildRequires:	%{?scl_prefix}jackson-databind
BuildRequires:	%{?scl_prefix}jackson-dataformat-yaml
BuildRequires:	%{?scl_prefix}jackson-dataformat-xml
BuildRequires:	%{?scl_prefix}jackson-annotations
BuildRequires:	%{?scl_prefix}jackson-module-jaxb-annotations
BuildRequires:	%{?scl_prefix_java_common}jansi
BuildRequires:	%{?scl_prefix}jeromq
BuildRequires:	%{?scl_prefix}apache-commons-csv
BuildRequires:	%{?scl_prefix}slf4j-ext
BuildRequires:	%{?scl_prefix_java_common}javassist
BuildRequires:	%{?scl_prefix_maven}cal10n
BuildRequires:	%{?scl_prefix}jopt-simple
# missing test dependency
#BuildRequires:	mvn(org.hamcrest:java-hamcrest)
%{?scl:Requires: %scl_runtime}

BuildArch:	noarch

%description
OHC - Off-Heap Concurrent hash map intended to store GBs of serialized data.

%package benchmark
Summary:	OHC benchmark executable
Requires:	time

%description benchmark
OHC benchmark executable.

%package core-j8
Summary:	OHC core - Java8 optimization

%description core-j8
OHC core - Java8 optimization.

%package jmh
Summary:	OHC core - micro benchmarks

%description jmh
Off-Heap concurrent hash map intended to store GBs of serialized data.

%package parent
Summary:	OHC Parent POM

%description parent
OHC Parent POM.

%package javadoc
Summary:	Javadoc for %{name}

%description javadoc
This package contains javadoc for %{name}.

%prep
%setup -q -n %{pkg_name}-%{version}

%{?scl:scl enable %{scl_maven} %{scl} - << "EOF"}
%pom_remove_plugin -r :cobertura-maven-plugin
%pom_remove_plugin -r :maven-assembly-plugin
%pom_remove_plugin -r :maven-dependency-plugin
%pom_remove_plugin -r :maven-javadoc-plugin
%pom_remove_plugin -r :maven-shade-plugin
%pom_remove_plugin -r :maven-source-plugin

%pom_xpath_set "pom:addClasspath" false ohc-benchmark
%pom_xpath_remove "pom:classpathPrefix" ohc-benchmark

# there is a missing test dependency since 0.6.1 version
%pom_remove_dep -r org.hamcrest:java-hamcrest
# remove file requiring the missing dependency
rm ohc-core/src/test/java/org/caffinitas/ohc/linked/FrequencySketchTest.java
%{?scl:EOF}

# TODO in SCL
# location of first binary to install
%global bin1loc %{pkg_name}-benchmark/src/main/sh/batch-bench.sh
# javadir for sed
%global myjdir \\/usr\\/share\\/java\\/
# jars for the classpath
%global classpath %{myjdir}ohc\\/ohc-core.jar:%{myjdir}ohc\\/ohc-benchmark.jar:%{myjdir}ohc\\/ohc-core-j8.jar:%{myjdir}metrics\\/metrics-core.jar:%{myjdir}metrics\\/metrics-graphite.jar:%{myjdir}metrics\\/metrics-ganglia.jar:%{myjdir}slf4j\\/slf4j-jdk14.jar:%{myjdir}slf4j\\/jdk14.jar:%{myjdir}slf4j\\/slf4j-nop.jar:%{myjdir}slf4j\\/slf4j-simple.jar:%{myjdir}slf4j\\/nop.jar:%{myjdir}slf4j\\/slf4j-api.jar:%{myjdir}slf4j\\/api.jar:%{myjdir}slf4j\\/simple.jar:%{myjdir}guava.jar:%{myjdir}jna.jar:%{myjdir}commons-cli.jar:%{myjdir}commons-math3.jar:%{myjdir}log4j.jar

# prepare scripts that will be installed
sed -i 's/script_dir=.*//g' %{bin1loc}
sed -i 's/base_dir=.*//g' %{bin1loc}
sed -i 's/version=.*//g' %{bin1loc}
sed -i 's/jar=.*$/cp=%{classpath}/g' %{bin1loc}
sed -i '0,/if \[ ! -f.*$/s///' %{bin1loc}
sed -i '0,/echo.*$/s///' %{bin1loc}
sed -i '0,/exit.*$/s///' %{bin1loc}
sed -i '0,/fi.*$/s///' %{bin1loc}
sed -i 's/java -jar $jar/java -cp $cp org.caffinitas.%{pkg_name}.benchmark.BenchmarkOHC /' %{bin1loc}
sed -i 's/echo "Cannot exe.*"/echo "Cannot execute ohc-benchmark jar file"/g' %{bin1loc}
sed -i 's/$jvm_arg -jar $jar "/$jvm_arg -cp $cp org.caffinitas.%{pkg_name}.benchmark.BenchmarkOHC "/g' %{bin1loc}

%build
%{?scl:scl enable %{scl_maven} %{scl} - << "EOF"}
# skip tests for now in SCL package
%mvn_build -s %{?scl:-f}
#%mvn_build -s -X -- -Dproject.build.sourceEncoding=UTF-8
%{?scl:EOF}

%install
%{?scl:scl enable %{scl_maven} %{scl} - << "EOF"}
%mvn_install
%{?scl:EOF}

%jpackage_script org.caffinitas.%{pkg_name}.benchmark.BenchmarkOHC "" "" %{pkg_name}:metrics-core:slf4j:guava:jna:commons-cli:commons-math3:log4j %{pkg_name}-benchmark true
cp -p %{pkg_name}-benchmark/src/main/sh/batch-bench.sh %{buildroot}%{_bindir}/%{pkg_name}-batch-benchmark
cp -p %{pkg_name}-benchmark/src/main/sh/consolidate-output.sh %{buildroot}%{_bindir}/%{pkg_name}-consolidate-output

%files -f .mfiles-%{pkg_name}-core
%doc CHANGES.txt README.rst
%license %{pkg_name}-core/LICENSE.txt

%files benchmark -f .mfiles-%{pkg_name}-benchmark
%doc %{pkg_name}-benchmark/NOTES.txt
%license %{pkg_name}-benchmark/LICENSE.txt
%attr(755, root, root) %{_bindir}/%{pkg_name}-benchmark
%attr(755, root, root) %{_bindir}/%{pkg_name}-batch-benchmark
%attr(755, root, root) %{_bindir}/%{pkg_name}-consolidate-output

%files core-j8 -f .mfiles-%{pkg_name}-core-j8
%license %{pkg_name}-core-j8/LICENSE.txt

%files jmh -f .mfiles-%{pkg_name}-jmh
%license %{pkg_name}-jmh/LICENSE.txt

%files parent -f .mfiles-%{pkg_name}-parent
%license LICENSE.txt

%files javadoc -f .mfiles-javadoc
%license LICENSE.txt

%changelog
* Thu Apr 20 2017 Tomas Repik <trepik@redhat.com> - 0.6.1-2
- scl conversion

* Wed Apr 19 2017 Tomas Repik <trepik@redhat.com> - 0.6.1-1
- version update, tests are back to normal

* Tue Aug 16 2016 Tomas Repik <trepik@redhat.com> - 0.4.5-1
- version update, tests are skipped

* Mon Mar 21 2016 Tomas Repik <trepik@redhat.com> - 0.4.2-4
- launchers revised, not final

* Wed Mar 16 2016 Tomas Repik <trepik@redhat.com> - 0.4.2-3
- launcher BenchmarkOHC installation
- benchmark scrips added

* Fri Feb 12 2016 Tomas Repik <trepik@redhat.com> - 0.4.2-2
- Updated build-dependencies

* Sat Feb 06 2016 gil cattaneo <puntogil@libero.it> 0.4.2-1
- update to 0.4.2

* Wed Jul 22 2015 gil cattaneo <puntogil@libero.it> 0.3.6-1
- initial rpm
