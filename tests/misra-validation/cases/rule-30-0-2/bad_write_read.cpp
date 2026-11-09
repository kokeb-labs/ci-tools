// Seeded violation: a write, then a read of the same file stream; std::flush is not a positioning operation.
#include <fstream>

namespace kv::rule_30_0_2::bad_write_read {

char write_then_read(std::fstream& file) {
  file << 'x' << std::flush;
  char c{};
  file >> c;  // seeded
  return c;
}

}  // namespace kv::rule_30_0_2::bad_write_read
