// Compliant near miss: a write, then seekg, then a read of the same stream.
#ifndef KV_RULE_30_0_2_OK_SEEKG_HPP
#define KV_RULE_30_0_2_OK_SEEKG_HPP

#include <fstream>

namespace kv::rule_30_0_2::ok_seekg {

inline char write_then_read(std::fstream& file) {
  file << 'x';
  static_cast<void>(file.seekg(0));
  char c{};
  file >> c;
  return c;
}

}  // namespace kv::rule_30_0_2::ok_seekg

#endif  // KV_RULE_30_0_2_OK_SEEKG_HPP
