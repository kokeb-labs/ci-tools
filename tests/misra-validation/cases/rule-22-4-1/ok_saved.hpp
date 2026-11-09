// Compliant near miss: errno is read and saved, then reset to zero; a local holds the error number.
#ifndef KV_RULE_22_4_1_OK_SAVED_HPP
#define KV_RULE_22_4_1_OK_SAVED_HPP

#include <cerrno>
#include <cstdint>

namespace kv::rule_22_4_1::ok_saved {

[[nodiscard]] inline std::int32_t take_error() {
  const std::int32_t saved = errno;
  errno = 0;
  return saved;
}

}  // namespace kv::rule_22_4_1::ok_saved

#endif  // KV_RULE_22_4_1_OK_SAVED_HPP
