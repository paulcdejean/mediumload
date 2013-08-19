# medium_config.rb

Facter.add("medium_config") do
  setcode do
    if File.exist? "/etc/mediumload.conf"
      true
    else
      false
    end
  end
end
