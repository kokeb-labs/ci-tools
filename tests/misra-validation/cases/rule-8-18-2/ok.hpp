// Compliant: the assignment is its own statement.
#ifndef KV_RULE_8_18_2_OK_HPP
#define KV_RULE_8_18_2_OK_HPP

#include <cstdint>

namespace kv::rule_8_18_2::ok {

inline bool latch(std::uint32_t& stored, std::uint32_t next) {
  stored = next;
  return stored != 0U;
}

}  // namespace kv::rule_8_18_2::ok

#endif  // KV_RULE_8_18_2_OK_HPP
