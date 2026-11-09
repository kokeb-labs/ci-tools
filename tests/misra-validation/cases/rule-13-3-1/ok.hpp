// Compliant: the overrider says override, and only the introducing declaration says virtual.
#ifndef KV_RULE_13_3_1_OK_HPP
#define KV_RULE_13_3_1_OK_HPP

#include <cstdint>

namespace kv::rule_13_3_1::ok {

class Port {
 public:
  Port() = default;
  Port(const Port&) = delete;
  Port(Port&&) = delete;
  Port& operator=(const Port&) = delete;
  Port& operator=(Port&&) = delete;
  virtual ~Port() = default;
  virtual std::uint32_t read() const = 0;
};

class Fake final : public Port {
 public:
  Fake() = default;
  Fake(const Fake&) = delete;
  Fake(Fake&&) = delete;
  Fake& operator=(const Fake&) = delete;
  Fake& operator=(Fake&&) = delete;
  ~Fake() override = default;
  std::uint32_t read() const override { return 1U; }
};

inline std::uint32_t sample(const Port& p) { return p.read(); }

}  // namespace kv::rule_13_3_1::ok

#endif  // KV_RULE_13_3_1_OK_HPP
