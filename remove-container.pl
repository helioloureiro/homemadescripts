#! /usr/bin/perl

my $pattern=$ARGV[0];

sub usage() {
    print "Use: $0 <container version>\n";
    print "Example: $0 10.4.0-a40f794\n";

}


if (length($pattern) == 0) {
    usage();
    exit(1);
}

my %remove_list;

open(DOCKER, "docker images |") or die "Impossible to run the command \"docker images\"";

foreach my $line (<DOCKER>){
    chomp $line;
    #print "LINE: $line\n";
    $line =~ s/  */ /g;
    my @parameters = split(/ /, $line);
    my $repo = $parameters[0];
    my $tag = $parameters[1];
    my $imageid = $parameters[2];
    next if ($tag !~ m/$pattern/);
    print "MATCHED: $repo:$tag\n";
    $remove_list{$imageid} += 1;
}

print "Removing containers: ";
foreach my $container (keys %remove_list) {
    print $container." ";
    `docker rmi -f $container`;
}
print "\n";
