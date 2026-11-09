// Compliant: the put position is set between the read and the write.
#ifndef KV_RULE_30_0_2_OK_HPP
#define KV_RULE_30_0_2_OK_HPP

#include <fstream>

namespace kv::rule_30_0_2::ok {

inline void patch(std::fstream& file) {
  char marker{};
  file >> marker;
  static_cast<void>(file.seekp(0));
  file << marker;
}

}  // namespace kv::rule_30_0_2::ok

#endif  // KV_RULE_30_0_2_OK_HPP
