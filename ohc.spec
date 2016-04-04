Name:          ohc
Version:       0.4.2
Release:       4%{?dist}
Summary:       Java large off heap cache 
License:       ASL 2.0
URL:           http://caffinitas.org/
Source0:       https://github.com/snazy/%{name}/archive/%{version}.tar.gz

BuildRequires: maven-local
BuildRequires: mvn(com.google.guava:guava)
BuildRequires: mvn(commons-cli:commons-cli)

# change to dropwizard for fedora 24
#BuildRequires: mvn(io.dropwizard.metrics:metrics-core)
BuildRequires: mvn(com.codahale.metrics:metrics-core)

BuildRequires: mvn(net.java.dev.jna:jna)
BuildRequires: mvn(net.jpountz.lz4:lz4)
BuildRequires: mvn(org.apache.commons:commons-math3)
BuildRequires: mvn(org.apache.felix:maven-bundle-plugin)
BuildRequires: mvn(org.apache.logging.log4j:log4j-api)
BuildRequires: mvn(org.apache.logging.log4j:log4j-core)
BuildRequires: mvn(org.apache.logging.log4j:log4j-slf4j-impl)
BuildRequires: mvn(org.openjdk.jmh:jmh-core)
BuildRequires: mvn(org.openjdk.jmh:jmh-generator-annprocess)
BuildRequires: mvn(org.slf4j:slf4j-api)
BuildRequires: mvn(org.testng:testng)
BuildRequires: mvn(org.xerial.snappy:snappy-java)
# missing in tests
BuildRequires: mvn(org.codehaus.mojo:exec-maven-plugin)

BuildArch:     noarch

%description
OHC - Off-Heap Concurrent hash map intended to store GBs of serialized data.

%package benchmark
Summary:   OHC benchmark executable
Requires:  time

%description benchmark
OHC benchmark executable.

%package core-j8
Summary:       OHC core - Java8 optimization

%description core-j8
OHC core - Java8 optimization.

%package jmh
Summary:       OHC core - micro benchmarks

%description jmh
Off-Heap concurrent hash map intended to store GBs of serialized data.

%package parent
Summary:       OHC Parent POM

%description parent
OHC Parent POM.

%package javadoc
Summary:       Javadoc for %{name}

%description javadoc
This package contains javadoc for %{name}.

%prep
%setup -q -n %{name}-%{version}

%pom_remove_plugin -r :cobertura-maven-plugin
%pom_remove_plugin -r :maven-assembly-plugin
%pom_remove_plugin -r :maven-dependency-plugin
%pom_remove_plugin -r :maven-javadoc-plugin
%pom_remove_plugin -r :maven-shade-plugin
%pom_remove_plugin -r :maven-source-plugin

%pom_xpath_set -r "pom:addClasspath" false
%pom_xpath_remove -r "pom:classpathPrefix"
#%%pom_xpath_remove -r "pom:mainClass"

#remove for fedora24
%pom_remove_dep io.dropwizard.metrics:metrics-core %{name}-benchmark
%pom_add_dep com.codahale.metrics:metrics-core %{name}-benchmark

# location of first binary to install
%global bin1loc %{name}-benchmark/src/main/sh/batch-bench.sh
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
sed -i 's/java -jar $jar/java -cp $cp org.caffinitas.%{name}.benchmark.BenchmarkOHC /' %{bin1loc}
sed -i 's/echo "Cannot exe.*"/echo "Cannot execute ohc-benchmark jar file"/g' %{bin1loc}
sed -i 's/$jvm_arg -jar $jar "/$jvm_arg -cp $cp org.caffinitas.%{name}.benchmark.BenchmarkOHC "/g' %{bin1loc}

%build
%mvn_build -s

%install
%mvn_install
%jpackage_script org.caffinitas.%{name}.benchmark.BenchmarkOHC "" "" %{name}:metrics-core:slf4j:guava:jna:commons-cli:commons-math3:log4j %{name}-benchmark true
cp -p %{name}-benchmark/src/main/sh/batch-bench.sh %{buildroot}%{_bindir}/%{name}-batch-benchmark
cp -p %{name}-benchmark/src/main/sh/consolidate-output.sh %{buildroot}%{_bindir}/%{name}-consolidate-output

%files -f .mfiles-%{name}-core
%doc CHANGES.txt README.rst notes-todos.txt
%license %{name}-core/LICENSE.txt

%files benchmark -f .mfiles-%{name}-benchmark
%doc %{name}-benchmark/NOTES.txt
%license %{name}-benchmark/LICENSE.txt
%attr(755, root, root) %{_bindir}/%{name}-benchmark
%attr(755, root, root) %{_bindir}/%{name}-batch-benchmark
%attr(755, root, root) %{_bindir}/%{name}-consolidate-output

%files core-j8 -f .mfiles-%{name}-core-j8
%license %{name}-core-j8/LICENSE.txt

%files jmh -f .mfiles-%{name}-jmh
%license %{name}-jmh/LICENSE.txt

%files parent -f .mfiles-%{name}-parent
%license LICENSE.txt

%files javadoc -f .mfiles-javadoc
%license LICENSE.txt

%changelog
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
