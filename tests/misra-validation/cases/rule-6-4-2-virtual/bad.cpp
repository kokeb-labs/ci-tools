// Seeded violation: overriding one virtual overload hides the other one in the derived class.
#include <cstdint>

namespace kv::rule_6_4_2_virtual::bad {

class Sink {
 public:
  virtual ~Sink() = default;
  virtual void put(std::int32_t value) = 0;
  virtual void put(std::int32_t value, std::int32_t weight) = 0;
};

class Logger : public Sink {
 public:
  void put(std::int32_t value) override;  // seeded

 private:
  std::int32_t last_{0};
};

void Logger::put(std::int32_t value) { last_ = value + 1; }

}  // namespace kv::rule_6_4_2_virtual::bad
