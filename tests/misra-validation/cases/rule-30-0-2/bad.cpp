// Seeded violation: a file stream written straight after a read, with no positioning call between.
#include <fstream>

namespace kv::rule_30_0_2::bad {

void patch(std::fstream& file) {
  char marker{};
  file >> marker;
  file << 'x';  // seeded
}

void patch_local() {
  std::fstream file{"/tmp/settings.bin"};
  char marker{};
  file >> marker;
  file << 'x';  // seeded
}

}  // namespace kv::rule_30_0_2::bad
