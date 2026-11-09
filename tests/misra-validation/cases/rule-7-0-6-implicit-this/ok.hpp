// Compliant: an integer constant that fits, passed to a member function that has no overload; the
// unqualified call names a member, so it is the class member access (*this).read (overload-independent).
#ifndef KV_RULE_7_0_6_IMPLICIT_THIS_OK_HPP
#define KV_RULE_7_0_6_IMPLICIT_THIS_OK_HPP

#include <cstdint>

namespace kv::rule_7_0_6_implicit_this::ok {

class Device {
 public:
  std::uint32_t poll() { return read(kBank, 0); }

 private:
  static constexpr std::uint8_t kBank = 9U;
  std::uint32_t read(std::uint8_t bank, std::uint32_t sdi) {
    return static_cast<std::uint32_t>(bank) ^ sdi;
  }
};

}  // namespace kv::rule_7_0_6_implicit_this::ok

#endif  // KV_RULE_7_0_6_IMPLICIT_THIS_OK_HPP
