#ifndef KV_RULE_6_4_2_VIRTUAL_OK_HPP
#define KV_RULE_6_4_2_VIRTUAL_OK_HPP

// Compliant: the derived class overrides every overload of the virtual function.
#include <cstdint>

namespace kv::rule_6_4_2_virtual::ok {

class Sink {
 public:
  Sink() = default;
  Sink(Sink const&) = delete;
  Sink(Sink&&) = delete;
  Sink& operator=(Sink const&) = delete;
  Sink& operator=(Sink&&) = delete;
  virtual ~Sink() = default;
  virtual void put(std::int32_t value) = 0;
  virtual void put(std::int32_t value, std::int32_t weight) = 0;
};

class Logger final : public Sink {
 public:
  void put(std::int32_t value) override { last_ = value; }
  void put(std::int32_t value, std::int32_t weight) override { last_ = (weight > 0) ? value : 0; }

 private:
  std::int32_t last_{0};
};

}  // namespace kv::rule_6_4_2_virtual::ok

#endif  // KV_RULE_6_4_2_VIRTUAL_OK_HPP
