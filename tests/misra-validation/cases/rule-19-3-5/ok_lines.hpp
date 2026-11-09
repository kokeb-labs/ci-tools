// Near miss: an argument over several lines, no directive in it.
#ifndef KV_RULE_19_3_5_OK_LINES_HPP
#define KV_RULE_19_3_5_OK_LINES_HPP

#include <cstdint>

#define KV_RULE_19_3_5_ID(X) (X)

namespace kv::rule_19_3_5::ok_lines {

inline std::uint32_t sum(std::uint32_t a, std::uint32_t b) {
  return KV_RULE_19_3_5_ID(
      a +
      b);
}

}  // namespace kv::rule_19_3_5::ok_lines

#undef KV_RULE_19_3_5_ID

#endif  // KV_RULE_19_3_5_OK_LINES_HPP
